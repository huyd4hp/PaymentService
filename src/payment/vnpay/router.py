from fastapi import APIRouter,Request,Depends,HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from .vnpay import vnpay,get_client_ip
from core import *
from .schema import PaymentForm,VNPayResponse
import requests 
from fastapi import Depends
from auth.dependencies import login_required
import json
from core.kafka import KafkaProducer

VNPayRouter = APIRouter(
    tags=["VNPay"]
)

@VNPayRouter.post('/payment',dependencies=[Depends(login_required)])
def create_booking(request:Request,payment:PaymentForm):
    # check order_id
    order_id = payment.booking_id
    response = requests.get(f'http://127.0.0.1:5050/api/v1/booking/{order_id}',headers={
        "Authorization":request.headers.get("Authorization")
    })
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=response.json())
    amount = response.json()['metadata']['total']
    order_desc = payment.booking_desc+f' | {response.json()['metadata']['seat']}'
    bank_code = payment.bank_code
    # language = payment.language
    language = 'vn'
    ipaddr = get_client_ip(request)
    # Build URL Payment
    vnp = vnpay()

    vnp.requestData['vnp_Version'] = '2.1.0'
    vnp.requestData['vnp_Command'] = 'pay'
    vnp.requestData['vnp_TmnCode'] = VNPAY_TMN_CODE
    vnp.requestData['vnp_Amount'] = amount * 100
    vnp.requestData['vnp_CurrCode'] = 'VND'
    vnp.requestData['vnp_TxnRef'] = order_id
    vnp.requestData['vnp_OrderInfo'] = order_desc 
    vnp.requestData['vnp_OrderType'] = 'other'
    if language and language != '':
        vnp.requestData['vnp_Locale'] = language
    else:
        vnp.requestData['vnp_Locale'] = 'vn'
    if bank_code and bank_code != "":
        vnp.requestData['vnp_BankCode'] = bank_code
    vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp.requestData['vnp_IpAddr'] = ipaddr
    vnp.requestData['vnp_ReturnUrl'] = RETURN_URL
    vnpay_payment_url = vnp.get_payment_url(VNPAY_PAYMENT_URL, VNPAY_HASH_SECRET_KEY)
    return vnpay_payment_url

@VNPayRouter.get("/payment_return")
async def payment_return(inputData: VNPayResponse = Depends()):
    try:
        vnp = vnpay()
        vnp.responseData = inputData.model_dump()
        if 'vnp_SecureHash' not in vnp.responseData:
            return JSONResponse(content={"title": "Kết quả thanh toán", "result": "Lỗi", "msg": "Thiếu vnp_SecureHash"})
        order_id = inputData.vnp_TxnRef  # booking id
        amount = inputData.vnp_Amount / 100
        order_desc = inputData.vnp_OrderInfo  # Booking desc
        seat_id = inputData.vnp_OrderInfo.split(" | ")[1]
        vnp_TransactionNo = inputData.vnp_TransactionNo
        vnp_ResponseCode = inputData.vnp_ResponseCode
        vnp_TransactionStatus = inputData.vnp_TransactionStatus
        vnp_TmnCode = VNPAY_TMN_CODE
        vnp_PayDate = inputData.vnp_PayDate
        vnp_BankCode = inputData.vnp_BankCode
        vnp_CardType = inputData.vnp_CardType

        if vnp.validate_response(VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == '00' and vnp_TransactionStatus == '00':
                producer = KafkaProducer(KAFKA_BOOTSTRAP_SERVERS="localhost:9092")
                await producer.connect()
                await producer.sendMessage(
                    Topic = "payment_return",
                    Key = "Paid".encode(),
                    Message= str(seat_id).encode()
                )
                await producer.close()
                return JSONResponse(content={"title": "Kết quả thanh toán",
                                             "result": "Thành công", "order_id": order_id,
                                             "amount": amount,
                                             "order_desc": order_desc,
                                             "vnp_TransactionNo": vnp_TransactionNo,
                                             "vnp_ResponseCode": vnp_ResponseCode})            
        else:
            if vnp_ResponseCode == '24' and vnp_TransactionStatus == '02':
                producer = KafkaProducer(KAFKA_BOOTSTRAP_SERVERS="localhost:9092")
                data = dict()
                data['seat'] = seat_id
                await producer.connect()
                await producer.sendMessage(
                    Topic = "payment_return",
                    Key = "Failed".encode(),
                    Message= str(json.dumps(data)).encode()
                )
                await producer.close()
            return JSONResponse(content=
                                {"title": "Kết quả thanh toán",
                                    "result": "Lỗi", "order_id": order_id,
                                    "amount": amount,
                                                "order_desc": order_desc,
                                                "vnp_TransactionNo": vnp_TransactionNo,
                                                "vnp_ResponseCode": vnp_ResponseCode,
                                                "vnp_TransactionStatus": vnp_TransactionStatus})
    except Exception as e:
        return JSONResponse(content={"title": "Kết quả thanh toán", "result": "", "error": str(e)})
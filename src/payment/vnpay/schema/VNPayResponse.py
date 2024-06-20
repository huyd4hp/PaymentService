from pydantic import BaseModel
from typing import Optional
class VNPayResponse(BaseModel):
    vnp_TxnRef: str
    vnp_Amount: int
    vnp_OrderInfo: str
    vnp_TransactionNo: str
    vnp_BankTranNo: Optional[str] = None
    vnp_ResponseCode: str
    vnp_TransactionStatus: str
    vnp_TransactionNo: str
    vnp_TmnCode: str
    vnp_PayDate: str
    vnp_BankCode: str
    vnp_CardType: str
    vnp_SecureHash: str 
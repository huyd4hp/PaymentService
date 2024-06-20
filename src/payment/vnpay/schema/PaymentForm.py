from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional,Any

class PaymentForm(BaseModel):
    booking_id:str = Field(max_length=250)
    # amount: int
    booking_desc: Optional[str] = Field(max_length=100, default=f"Thanh toán hoá đơn {datetime.now()}")
    bank_code: Optional[str] = Field(max_length=20, default=None)
    language: str = Field(max_length=2,default=None)

from pydantic import BaseModel

class PaymentSubscription(BaseModel):
    identifier: str
    amount: str
    currency: str

from sqlalchemy import Column,String,Float,Date, func, ForeignKey
from connection.config import base
from sqlalchemy.orm import relationship

class billRegistrastion(base):  
    __tablename__ = "bill"
    bill_number = Column(String(20), primary_key=True, nullable=False)
    total_price = Column(Float(), nullable=False)
    entry_date = Column(Date(), default=func.current_date(), nullable=False)
    due = Column(Float(), nullable=False)
    client_name = Column(String(30), nullable=False)
    client_phone = Column(String(20), nullable=False)
    payment = Column(Float())
    document = Column(String(50), ForeignKey('worker.document') ,nullable=False)
    
    tphone = relationship("phoneRegistrastion", back_populates="tbill")
    tworker = relationship("workerRegistrastion", back_populates="tbill")


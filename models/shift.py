from sqlalchemy import String, Column, DateTime, Float, ForeignKey
from connection.config import base
from sqlalchemy.orm import relationship

class shiftRegistration(base):
    __tablename__ = "shift"
    ref_shift = Column(String(60), primary_key=True)
    document = Column(String(30), ForeignKey("worker.document"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    finish_time = Column(DateTime)
    total_received = Column(Float)
    total_gain = Column(Float)

    tworker = relationship("workerRegistrastion", back_populates="tshift")
    tdelivery = relationship("deliveryRegistration", back_populates="tshift")
    toutflow = relationship("outflowRegistration", back_populates="tshift")
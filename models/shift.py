from sqlalchemy import String, Column, DateTime, Float, ForeignKey, Date, func
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
    date_shift = Column(Date(), default=func.current_date(), nullable=False)

    tbill = relationship("billRegistrastion", back_populates="tshift")
    tworker = relationship("workerRegistrastion", back_populates="tshift")
    tdelivery = relationship("deliveryRegistration", back_populates="tshift")
    toutflow = relationship("outflowRegistration", back_populates="tshift")
    treparation = relationship("reparationRegistration", back_populates="tshift")
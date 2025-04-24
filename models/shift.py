from sqlalchemy import String, Column, DateTime, Float, ForeignKey, Date, func, Integer
from connection.config import base
from sqlalchemy.orm import relationship
from datetime import date

class shiftRegistration(base):
    __tablename__ = "shift"
    ref_shift = Column(String(60), primary_key=True)
    id = Column(String(80), ForeignKey("worker.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    finish_time = Column(DateTime)
    total_received = Column(Float)
    total_gain = Column(Float)
    total_outs = Column(Float)
    total_cash = Column(Float)
    total_platform = Column(Float)
    date_shift = Column(Date(), default=date.today, nullable=False)
    ref_premises = Column(Integer, ForeignKey("premises.ref_premises"), nullable=True)

    tbill = relationship("billRegistrastion", back_populates="tshift")
    tworker = relationship("workerRegistration", back_populates="tshift")
    tdelivery = relationship("deliveryRegistration", back_populates="tshift")
    toutflow = relationship("outflowRegistration", back_populates="tshift")
    treparation = relationship("reparationRegistration", back_populates="tshift")
    tpremises = relationship("premisesRegistration", back_populates="tshift")
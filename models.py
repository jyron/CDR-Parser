from sqlalchemy import Column, Integer, String
from database import Base


class UsageRecord(Base):
    """Normalized usage record model"""
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    mnc = Column(Integer, nullable=True)
    bytes_used = Column(Integer, nullable=True)
    dmcc = Column(String, nullable=True)
    cellid = Column(Integer, nullable=True)
    ip = Column(String, nullable=True)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "mnc": self.mnc,
            "bytes_used": self.bytes_used,
            "dmcc": self.dmcc,
            "cellid": self.cellid,
            "ip": self.ip
        }


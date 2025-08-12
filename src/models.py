from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base

class ModerationRequest(Base):
    __tablename__ = "moderation_requests"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  
    content_url = Column(String, nullable=True)    
    content_hash = Column(String, nullable=True)        
    status = Column(Enum("pending", "completed", name="notification_status"), default="pending")  
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    results = relationship("ModerationResult", back_populates="request", cascade="all, delete-orphan")
    notifications = relationship("NotificationLog", back_populates="request", cascade="all, delete-orphan")

    def get_content(self):
        if self.content_type == "image":
            return self.content_url
        elif self.content_type == "text":
            return self.content
        return None


class ModerationResult(Base):
    __tablename__ = "moderation_results"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"), nullable=False)
    classification = Column(String, nullable=False)  
    confidence = Column(Float, nullable=False)
    reasoning = Column(String, nullable=True)        
    llm_response = Column(JSON, nullable=True)      

    request = relationship("ModerationRequest", back_populates="results")


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"), nullable=False)
    channel = Column(String, nullable=False)         
    status = Column(Enum("pending", "send", name="moderation_status"), default="pending")      
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    request = relationship("ModerationRequest", back_populates="notifications")

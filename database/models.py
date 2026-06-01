from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Text, Boolean, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum

# Базовий клас для таблиць
class Base(DeclarativeBase):
    """Базовий клас для всіх моделей [cite: 5]"""
    pass

# Клас зі списком станів
class Status(str,PyEnum):
    '''Клас зі списком станів'''

    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    DRAFT = "DRAFT"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"
    ACTIVE = "ACTIVE"

# Клас зі списком адмінських привілеїв
class AdminPrivilege(str, PyEnum):
    """Клас зі списком адмінських привілеїв"""
    SUPERADMIN = "SUPERADMIN"
    ADMIN = "ADMIN"


# Клас з таблицею користувачів
class User(Base):
    '''Клас з таблицею користувачів'''

    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    language: Mapped[str] = mapped_column(String(5), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    admin_privilege: Mapped[Optional[AdminPrivilege]] = mapped_column(SAEnum(AdminPrivilege, native_enum=False),default=None)

    # Зв'язки
    questions: Mapped[List["SupportQuestion"]] = relationship(back_populates="user")
    workshop_requests: Mapped[List["WorkshopOpeningRequest"]] = relationship(back_populates="user")
    mobile_requests: Mapped[List["MobileWorkshopRequest"]] = relationship(back_populates="user")

# Клас з таблицею питань
class SupportQuestion(Base):
    '''Клас з таблицею питань'''

    __tablename__ = "questions"
    
    question_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Status] = mapped_column(
        SAEnum(Status, name="status", native_enum=True), 
        default=Status.NEW,
        server_default="NEW"
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="questions")

# Клас з анкетами для відкриття майстерні
class WorkshopOpeningRequest(Base):
    '''Клас з анкетами для відкриття майстерні'''

    __tablename__ = "workshop_opening_requests"
    
    request_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))

    country: Mapped[Optional[str]] = mapped_column(String(100))
    region: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    church_name: Mapped[Optional[str]] = mapped_column(String(255))
    known_information: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Status] = mapped_column(
        SAEnum(Status, name="status", native_enum=True), 
        default=Status.NEW,
        server_default="NEW"
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="workshop_requests")

# Клас з анкетами на запит мобільної майстерні
class MobileWorkshopRequest(Base):
    '''Клас з анкетами на запит мобільної майстерні'''

    __tablename__ = "mobile_workshop_requests"
    
    request_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    region: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    organization: Mapped[Optional[str]] = mapped_column(String(255))
    purpose: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Status] = mapped_column(
        SAEnum(Status, name="status", native_enum=True), 
        default=Status.NEW,
        server_default="NEW"
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="mobile_requests")

# Клас з FAQ запитаннями
class FAQQuestion(Base):
    '''Клас з FAQ запитаннями'''

    __tablename__ = "faq_questions"
    
    question_id: Mapped[int] = mapped_column(primary_key=True)
    language: Mapped[str] = mapped_column(String(5))
    category: Mapped[str] = mapped_column(String(100))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)

# Клас з майстернями
class Workshop(Base):
    '''Клас з майстернями'''

    __tablename__ = "workshops"
    
    workshop_id: Mapped[int] = mapped_column(primary_key=True)
    language: Mapped[str] = mapped_column(String(5))
    country: Mapped[str] = mapped_column(String(100))
    region: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    church_name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(Text)
    workshop_leader: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(20))
    status: Mapped[Status] = mapped_column(
        SAEnum(Status, name="status", native_enum=True), 
        default=Status.NEW,
        server_default="NEW"
    )
    media_message_id: Mapped[Optional[int]] = mapped_column(BigInteger)

# Клас з загальною інформацією
class GeneralInformation(Base):
    """Клас з загальною інформацією"""

    __tablename__ = "general_information"
    
    information_id: Mapped[int] = mapped_column(primary_key=True)
    language: Mapped[str] = mapped_column(String(5))
    category: Mapped[str] = mapped_column(String(100))
    information: Mapped[str] = mapped_column(Text)
    media_message_id: Mapped[Optional[int]] = mapped_column(BigInteger)
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.models import GenderEnum, ReportReasonEnum

# --- USER ---
class UserCreate(BaseModel):
    gender: Optional[GenderEnum] = None
    age_range: Optional[str] = None

class UserOut(BaseModel):
    id: UUID
    anonymous_name: str
    gender: Optional[GenderEnum]
    age_range: Optional[str]
    is_listening: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- FILTROS DE MATCH ---
class MatchFilters(BaseModel):
    gender: Optional[GenderEnum] = None
    age_range: Optional[str] = None
    exclude_city: Optional[bool] = True   # por padrão esconde cidade

# --- MENSAGEM ---
class MessageOut(BaseModel):
    id: UUID
    sender_id: UUID
    content: Optional[str]
    audio_url: Optional[str]
    sent_at: datetime

    class Config:
        from_attributes = True

# --- CONVERSA ---
class ConversationOut(BaseModel):
    id: UUID
    user_a_id: UUID
    user_b_id: UUID
    started_at: datetime
    is_active: bool
    messages: list[MessageOut] = []

    class Config:
        from_attributes = True

# --- DENÚNCIA ---
class ReportCreate(BaseModel):
    reported_id: UUID
    reason: ReportReasonEnum
    description: Optional[str] = None

class ReportOut(BaseModel):
    id: UUID
    reason: ReportReasonEnum
    created_at: datetime

    class Config:
        from_attributes = True

# --- BLOQUEIO ---
class BlockCreate(BaseModel):
    blocked_id: UUID

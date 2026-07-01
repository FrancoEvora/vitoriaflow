from datetime import datetime
from pydantic import BaseModel, Field


class LeadCreate(BaseModel):
    name: str
    phone: str | None = None
    source: str | None = None
    development_name: str | None = None
    objective: str = "indefinido"
    budget_entry: str | None = None
    budget_installment: str | None = None
    purchase_timeline: str | None = None
    knows_development: bool = False
    main_objection: str | None = None


class LeadOut(BaseModel):
    id: int
    name: str
    phone: str | None
    source: str | None
    objective: str
    temperature: str
    score: int
    status: str
    main_objection: str | None
    next_action: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BrokerOut(BaseModel):
    id: int
    name: str
    phone: str
    role: str
    active: bool

    model_config = {"from_attributes": True}


class SimulateMessageIn(BaseModel):
    from_phone: str = Field(..., examples=["5516999999999"])
    text: str = Field(..., examples=["Tenho um lead"])
    profile_name: str | None = Field(default="Corretor Teste")


class SimulateMessageOut(BaseModel):
    reply: str

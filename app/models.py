from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False)
    phone = Column(String(32), unique=True, nullable=False, index=True)
    email = Column(String(160), nullable=True)
    role = Column(String(32), default="broker", nullable=False)  # admin | manager | broker
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    leads = relationship("Lead", back_populates="broker")


class Development(Base):
    __tablename__ = "developments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False, unique=True)
    city = Column(String(160), nullable=True)
    status = Column(String(80), default="ativo", nullable=False)
    description = Column(Text, nullable=True)
    sales_arguments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    leads = relationship("Lead", back_populates="development")
    materials = relationship("Material", back_populates="development")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False, index=True)
    phone = Column(String(32), nullable=True, index=True)
    source = Column(String(120), nullable=True)
    development_id = Column(Integer, ForeignKey("developments.id"), nullable=True)
    broker_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    objective = Column(String(80), default="indefinido", nullable=False)
    budget_entry = Column(String(80), nullable=True)
    budget_installment = Column(String(80), nullable=True)
    purchase_timeline = Column(String(120), nullable=True)
    knows_development = Column(Boolean, default=False, nullable=False)

    temperature = Column(String(20), default="frio", nullable=False)  # quente | morno | frio
    score = Column(Integer, default=0, nullable=False)
    status = Column(String(40), default="novo", nullable=False)
    main_objection = Column(String(180), nullable=True)
    next_action = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    broker = relationship("User", back_populates="leads")
    development = relationship("Development", back_populates="leads")
    interactions = relationship("Interaction", back_populates="lead", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="lead", cascade="all, delete-orphan")
    recommendations = relationship("LeadRecommendation", back_populates="lead", cascade="all, delete-orphan")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    broker_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    direction = Column(String(20), nullable=False)  # inbound | outbound | system
    channel = Column(String(40), default="whatsapp", nullable=False)
    message = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    lead = relationship("Lead", back_populates="interactions")
    broker = relationship("User")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    broker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_type = Column(String(60), default="follow_up", nullable=False)
    description = Column(Text, nullable=False)
    due_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(40), default="aberta", nullable=False)  # aberta | concluida | cancelada
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    lead = relationship("Lead", back_populates="tasks")
    broker = relationship("User")


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    development_id = Column(Integer, ForeignKey("developments.id"), nullable=True)
    title = Column(String(180), nullable=False)
    type = Column(String(60), nullable=False)  # video | mapa | tabela | imagem | pdf | faq
    url = Column(Text, nullable=True)
    use_case = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    development = relationship("Development", back_populates="materials")


class LeadRecommendation(Base):
    __tablename__ = "lead_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    recommendation_type = Column(String(60), default="estrategia", nullable=False)
    diagnosis = Column(Text, nullable=False)
    strategy = Column(Text, nullable=False)
    script = Column(Text, nullable=False)
    materials = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    lead = relationship("Lead", back_populates="recommendations")


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    broker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    phone = Column(String(32), index=True, nullable=False)
    topic = Column(String(60), default="idle", nullable=False)
    state = Column(String(80), default="idle", nullable=False)
    payload = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    broker = relationship("User")

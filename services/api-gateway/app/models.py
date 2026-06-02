from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    customer_text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="NEW", index=True)
    created_by: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    analysis: Mapped["TicketAnalysis | None"] = relationship(back_populates="ticket", cascade="all, delete-orphan")
    evidence: Mapped[list["RetrievedEvidence"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")
    drafts: Mapped[list["Draft"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")
    audit_logs: Mapped[list["WorkflowAuditLog"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")


class TicketAnalysis(Base):
    __tablename__ = "ticket_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[str] = mapped_column(String(64), ForeignKey("tickets.ticket_id"), unique=True, index=True)
    classification: Mapped[dict] = mapped_column(JSON)
    urgency: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    ticket: Mapped[Ticket] = relationship(back_populates="analysis")


class RetrievedEvidence(Base):
    __tablename__ = "retrieved_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[str] = mapped_column(String(64), ForeignKey("tickets.ticket_id"), index=True)
    policy_id: Mapped[str] = mapped_column(String(64))
    chunk_id: Mapped[str] = mapped_column(String(256))
    title: Mapped[str] = mapped_column(String(256))
    section: Mapped[str] = mapped_column(String(128))
    score: Mapped[float]
    text: Mapped[str] = mapped_column(Text)
    item_metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    ticket: Mapped[Ticket] = relationship(back_populates="evidence")


class Draft(Base):
    __tablename__ = "drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[str] = mapped_column(String(64), ForeignKey("tickets.ticket_id"), index=True)
    draft: Mapped[dict] = mapped_column(JSON)
    edited_draft_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    ticket: Mapped[Ticket] = relationship(back_populates="drafts")


class ReviewAction(Base):
    __tablename__ = "review_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[str] = mapped_column(String(64), index=True)
    employee_id: Mapped[str] = mapped_column(String(64))
    role: Mapped[str] = mapped_column(String(32))
    action: Mapped[str] = mapped_column(String(32))
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class WorkflowAuditLog(Base):
    __tablename__ = "workflow_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[str] = mapped_column(String(64), ForeignKey("tickets.ticket_id"), index=True)
    actor_employee_id: Mapped[str] = mapped_column(String(64))
    actor_role: Mapped[str] = mapped_column(String(32))
    action: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    ticket: Mapped[Ticket] = relationship(back_populates="audit_logs")


class WorkerJobResult(Base):
    __tablename__ = "worker_job_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    ticket_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

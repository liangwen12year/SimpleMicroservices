from __future__ import annotations

from typing import Optional, Annotated
from uuid import UUID, uuid4
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, StringConstraints
from enum import Enum
from .person import UNIType

# Grade type: letter grade or numeric
GradeType = Annotated[str, StringConstraints(pattern=r"^[A-F][+-]?$|^\d{1,3}(\.\d{1,2})?$")]


class EnrollmentStatus(str, Enum):
    """Enrollment status enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    DROPPED = "dropped"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"


class EnrollmentBase(BaseModel):
    student_uni: UNIType = Field(
        ...,
        description="Columbia University UNI of the enrolled student.",
        json_schema_extra={"example": "abc1234"},
    )
    course_id: UUID = Field(
        ...,
        description="ID of the course being enrolled in.",
        json_schema_extra={"example": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"},
    )
    enrollment_date: date = Field(
        ...,
        description="Date when the student enrolled in the course.",
        json_schema_extra={"example": "2024-08-15"},
    )
    status: EnrollmentStatus = Field(
        default=EnrollmentStatus.PENDING,
        description="Current enrollment status.",
        json_schema_extra={"example": "active"},
    )
    grade: Optional[GradeType] = Field(
        None,
        description="Final grade received (letter grade or numeric score).",
        json_schema_extra={"example": "A+"},
    )
    credits_earned: Optional[int] = Field(
        None,
        ge=0,
        description="Number of credits earned for this enrollment.",
        json_schema_extra={"example": 3},
    )
    tuition_paid: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Amount of tuition paid for this enrollment.",
        json_schema_extra={"example": "1500.00"},
    )
    payment_date: Optional[date] = Field(
        None,
        description="Date when tuition was paid.",
        json_schema_extra={"example": "2024-08-20"},
    )
    completion_date: Optional[date] = Field(
        None,
        description="Date when the course was completed.",
        json_schema_extra={"example": "2024-12-15"},
    )
    withdrawal_date: Optional[date] = Field(
        None,
        description="Date when the student withdrew from the course.",
        json_schema_extra={"example": "2024-10-15"},
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about this enrollment.",
        json_schema_extra={"example": "Student requested special accommodations."},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "student_uni": "abc1234",
                    "course_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                    "enrollment_date": "2024-08-15",
                    "status": "active",
                    "grade": None,
                    "credits_earned": None,
                    "tuition_paid": "1500.00",
                    "payment_date": "2024-08-20",
                    "completion_date": None,
                    "withdrawal_date": None,
                    "notes": "Student requested special accommodations.",
                }
            ]
        }
    }


class EnrollmentCreate(EnrollmentBase):
    """Creation payload for an Enrollment."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "student_uni": "xy123",
                    "course_id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                    "enrollment_date": "2024-09-01",
                    "status": "pending",
                    "tuition_paid": "1800.00",
                    "payment_date": "2024-09-05",
                    "notes": "Transfer student from another institution.",
                }
            ]
        }
    }


class EnrollmentUpdate(BaseModel):
    """Partial update for an Enrollment; supply only fields to change."""
    student_uni: Optional[UNIType] = Field(
        None, description="Columbia University UNI of the enrolled student.", json_schema_extra={"example": "abc1234"}
    )
    course_id: Optional[UUID] = Field(
        None, description="ID of the course being enrolled in.", json_schema_extra={"example": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"}
    )
    status: Optional[EnrollmentStatus] = Field(
        None, description="Enrollment status.", json_schema_extra={"example": "completed"}
    )
    grade: Optional[GradeType] = Field(None, json_schema_extra={"example": "A"})
    credits_earned: Optional[int] = Field(None, ge=0, json_schema_extra={"example": 3})
    tuition_paid: Optional[Decimal] = Field(None, ge=0, json_schema_extra={"example": "1500.00"})
    payment_date: Optional[date] = Field(None, json_schema_extra={"example": "2024-08-20"})
    completion_date: Optional[date] = Field(None, json_schema_extra={"example": "2024-12-15"})
    withdrawal_date: Optional[date] = Field(None, json_schema_extra={"example": "2024-10-15"})
    notes: Optional[str] = Field(None, json_schema_extra={"example": "Updated notes"})

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"student_uni": "abc1234", "course_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", "status": "completed"},
                {"status": "completed", "grade": "A", "completion_date": "2024-12-15"},
                {"status": "dropped", "withdrawal_date": "2024-10-15"},
                {"tuition_paid": "1500.00", "payment_date": "2024-08-20"},
                {"notes": "Student completed with honors."},
            ]
        }
    }


class EnrollmentRead(EnrollmentBase):
    """Server representation returned to clients."""
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Enrollment ID.",
        json_schema_extra={"example": "cccccccc-cccc-4ccc-8ccc-cccccccccccc"},
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-01-15T10:20:30Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-01-16T12:00:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
                    "student_uni": "abc1234",
                    "course_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                    "enrollment_date": "2024-08-15",
                    "status": "completed",
                    "grade": "A+",
                    "credits_earned": 3,
                    "tuition_paid": "1500.00",
                    "payment_date": "2024-08-20",
                    "completion_date": "2024-12-15",
                    "withdrawal_date": None,
                    "notes": "Student completed with honors.",
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }
    }
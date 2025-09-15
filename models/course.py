from __future__ import annotations

from typing import Optional, List, Annotated
from uuid import UUID, uuid4
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, StringConstraints

# Course code pattern: 2-4 letters + 3-4 digits (e.g., CS101, MATH2001)
CourseCodeType = Annotated[str, StringConstraints(pattern=r"^[A-Z]{2,4}\d{3,4}$")]


class CourseBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="Persistent Course ID (server-generated).",
        json_schema_extra={"example": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"},
    )
    code: CourseCodeType = Field(
        ...,
        description="Course code (2-4 uppercase letters + 3-4 digits).",
        json_schema_extra={"example": "CS101"},
    )
    title: str = Field(
        ...,
        description="Course title.",
        json_schema_extra={"example": "Introduction to Computer Science"},
    )
    description: Optional[str] = Field(
        None,
        description="Detailed course description.",
        json_schema_extra={"example": "An introduction to fundamental concepts in computer science including algorithms, data structures, and programming."},
    )
    credits: int = Field(
        ...,
        ge=1,
        le=6,
        description="Number of credit hours (1-6).",
        json_schema_extra={"example": 3},
    )
    department: str = Field(
        ...,
        description="Academic department offering the course.",
        json_schema_extra={"example": "Computer Science"},
    )
    instructor: Optional[str] = Field(
        None,
        description="Primary instructor name.",
        json_schema_extra={"example": "Dr. Jane Smith"},
    )
    semester: str = Field(
        ...,
        description="Semester and year (e.g., Fall 2024, Spring 2025).",
        json_schema_extra={"example": "Fall 2024"},
    )
    start_date: Optional[date] = Field(
        None,
        description="Course start date.",
        json_schema_extra={"example": "2024-09-01"},
    )
    end_date: Optional[date] = Field(
        None,
        description="Course end date.",
        json_schema_extra={"example": "2024-12-15"},
    )
    max_enrollment: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum number of students allowed to enroll.",
        json_schema_extra={"example": 30},
    )
    current_enrollment: int = Field(
        default=0,
        ge=0,
        description="Current number of enrolled students.",
        json_schema_extra={"example": 25},
    )
    tuition_fee: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Tuition fee for the course.",
        json_schema_extra={"example": "1500.00"},
    )
    prerequisites: List[str] = Field(
        default_factory=list,
        description="List of prerequisite course codes.",
        json_schema_extra={"example": ["MATH101", "ENG101"]},
    )
    is_active: bool = Field(
        default=True,
        description="Whether the course is currently active and accepting enrollments.",
        json_schema_extra={"example": True},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                    "code": "CS101",
                    "title": "Introduction to Computer Science",
                    "description": "An introduction to fundamental concepts in computer science including algorithms, data structures, and programming.",
                    "credits": 3,
                    "department": "Computer Science",
                    "instructor": "Dr. Jane Smith",
                    "semester": "Fall 2024",
                    "start_date": "2024-09-01",
                    "end_date": "2024-12-15",
                    "max_enrollment": 30,
                    "current_enrollment": 25,
                    "tuition_fee": "1500.00",
                    "prerequisites": ["MATH101", "ENG101"],
                    "is_active": True,
                }
            ]
        }
    }


class CourseCreate(CourseBase):
    """Creation payload for a Course."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                    "code": "MATH2001",
                    "title": "Calculus I",
                    "description": "Introduction to differential and integral calculus.",
                    "credits": 4,
                    "department": "Mathematics",
                    "instructor": "Prof. John Doe",
                    "semester": "Spring 2025",
                    "start_date": "2025-01-15",
                    "end_date": "2025-05-15",
                    "max_enrollment": 40,
                    "tuition_fee": "1800.00",
                    "prerequisites": ["MATH101"],
                    "is_active": True,
                }
            ]
        }
    }


class CourseUpdate(BaseModel):
    """Partial update for a Course; supply only fields to change."""
    code: Optional[CourseCodeType] = Field(
        None, description="Course code.", json_schema_extra={"example": "CS102"}
    )
    title: Optional[str] = Field(None, json_schema_extra={"example": "Advanced Computer Science"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "Advanced topics in computer science."})
    credits: Optional[int] = Field(None, ge=1, le=6, json_schema_extra={"example": 4})
    department: Optional[str] = Field(None, json_schema_extra={"example": "Computer Science"})
    instructor: Optional[str] = Field(None, json_schema_extra={"example": "Dr. Alice Johnson"})
    semester: Optional[str] = Field(None, json_schema_extra={"example": "Summer 2025"})
    start_date: Optional[date] = Field(None, json_schema_extra={"example": "2025-06-01"})
    end_date: Optional[date] = Field(None, json_schema_extra={"example": "2025-08-15"})
    max_enrollment: Optional[int] = Field(None, ge=1, json_schema_extra={"example": 35})
    tuition_fee: Optional[Decimal] = Field(None, ge=0, json_schema_extra={"example": "1600.00"})
    prerequisites: Optional[List[str]] = Field(
        None,
        description="Replace the entire list of prerequisites.",
        json_schema_extra={"example": ["MATH101", "CS101"]},
    )
    is_active: Optional[bool] = Field(None, json_schema_extra={"example": False})

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"title": "Advanced Computer Science", "credits": 4},
                {"instructor": "Dr. Alice Johnson", "max_enrollment": 35},
                {"is_active": False},
                {
                    "prerequisites": ["MATH101", "CS101"],
                    "tuition_fee": "1600.00"
                },
            ]
        }
    }


class CourseRead(CourseBase):
    """Server representation returned to clients."""
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Course ID.",
        json_schema_extra={"example": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"},
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
                    "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                    "code": "CS101",
                    "title": "Introduction to Computer Science",
                    "description": "An introduction to fundamental concepts in computer science including algorithms, data structures, and programming.",
                    "credits": 3,
                    "department": "Computer Science",
                    "instructor": "Dr. Jane Smith",
                    "semester": "Fall 2024",
                    "start_date": "2024-09-01",
                    "end_date": "2024-12-15",
                    "max_enrollment": 30,
                    "current_enrollment": 25,
                    "tuition_fee": "1500.00",
                    "prerequisites": ["MATH101", "ENG101"],
                    "is_active": True,
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }
    }
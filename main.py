from __future__ import annotations

import os
import socket
from datetime import datetime

from typing import Dict, List
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi import Query, Path
from typing import Optional

from models.person import PersonCreate, PersonRead, PersonUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate
from models.course import CourseCreate, CourseRead, CourseUpdate
from models.enrollment import EnrollmentCreate, EnrollmentRead, EnrollmentUpdate, EnrollmentStatus
from models.health import Health

port = int(os.environ.get("FASTAPIPORT", 8000))

# -----------------------------------------------------------------------------
# Fake in-memory "databases"
# -----------------------------------------------------------------------------
persons: Dict[UUID, PersonRead] = {}
addresses: Dict[UUID, AddressRead] = {}
courses: Dict[UUID, CourseRead] = {}
enrollments: Dict[UUID, EnrollmentRead] = {}

app = FastAPI(
    title="Person/Address API",
    description="Demo FastAPI app using Pydantic v2 models for Person and Address",
    version="0.1.0",
)

# -----------------------------------------------------------------------------
# Address endpoints
# -----------------------------------------------------------------------------

def make_health(echo: Optional[str], path_echo: Optional[str]=None) -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=datetime.utcnow().isoformat() + "Z",
        ip_address=socket.gethostbyname(socket.gethostname()),
        echo=echo,
        path_echo=path_echo
    )

@app.get("/health", response_model=Health)
def get_health_no_path(echo: str | None = Query(None, description="Optional echo string")):
    # Works because path_echo is optional in the model
    return make_health(echo=echo, path_echo=None)

@app.get("/health/{path_echo}", response_model=Health)
def get_health_with_path(
    path_echo: str = Path(..., description="Required echo in the URL path"),
    echo: str | None = Query(None, description="Optional echo string"),
):
    return make_health(echo=echo, path_echo=path_echo)

@app.post("/addresses", response_model=AddressRead, status_code=201)
def create_address(address: AddressCreate):
    if address.id in addresses:
        raise HTTPException(status_code=400, detail="Address with this ID already exists")
    addresses[address.id] = AddressRead(**address.model_dump())
    return addresses[address.id]

@app.get("/addresses", response_model=List[AddressRead])
def list_addresses(
    street: Optional[str] = Query(None, description="Filter by street"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state/region"),
    postal_code: Optional[str] = Query(None, description="Filter by postal code"),
    country: Optional[str] = Query(None, description="Filter by country"),
):
    results = list(addresses.values())

    if street is not None:
        results = [a for a in results if a.street == street]
    if city is not None:
        results = [a for a in results if a.city == city]
    if state is not None:
        results = [a for a in results if a.state == state]
    if postal_code is not None:
        results = [a for a in results if a.postal_code == postal_code]
    if country is not None:
        results = [a for a in results if a.country == country]

    return results

@app.get("/addresses/{address_id}", response_model=AddressRead)
def get_address(address_id: UUID):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    return addresses[address_id]

@app.patch("/addresses/{address_id}", response_model=AddressRead)
def update_address(address_id: UUID, update: AddressUpdate):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    stored = addresses[address_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    addresses[address_id] = AddressRead(**stored)
    return addresses[address_id]

# -----------------------------------------------------------------------------
# Person endpoints
# -----------------------------------------------------------------------------
@app.post("/persons", response_model=PersonRead, status_code=201)
def create_person(person: PersonCreate):
    # Each person gets its own UUID; stored as PersonRead
    person_read = PersonRead(**person.model_dump())
    persons[person_read.id] = person_read
    return person_read

@app.get("/persons", response_model=List[PersonRead])
def list_persons(
    uni: Optional[str] = Query(None, description="Filter by Columbia UNI"),
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    birth_date: Optional[str] = Query(None, description="Filter by date of birth (YYYY-MM-DD)"),
    city: Optional[str] = Query(None, description="Filter by city of at least one address"),
    country: Optional[str] = Query(None, description="Filter by country of at least one address"),
):
    results = list(persons.values())

    if uni is not None:
        results = [p for p in results if p.uni == uni]
    if first_name is not None:
        results = [p for p in results if p.first_name == first_name]
    if last_name is not None:
        results = [p for p in results if p.last_name == last_name]
    if email is not None:
        results = [p for p in results if p.email == email]
    if phone is not None:
        results = [p for p in results if p.phone == phone]
    if birth_date is not None:
        results = [p for p in results if str(p.birth_date) == birth_date]

    # nested address filtering
    if city is not None:
        results = [p for p in results if any(addr.city == city for addr in p.addresses)]
    if country is not None:
        results = [p for p in results if any(addr.country == country for addr in p.addresses)]

    return results

@app.get("/persons/{person_id}", response_model=PersonRead)
def get_person(person_id: UUID):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    return persons[person_id]

@app.patch("/persons/{person_id}", response_model=PersonRead)
def update_person(person_id: UUID, update: PersonUpdate):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    stored = persons[person_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    persons[person_id] = PersonRead(**stored)
    return persons[person_id]


# -----------------------------------------------------------------------------
# Course endpoints
# -----------------------------------------------------------------------------

@app.post("/courses", response_model=CourseRead, status_code=201)
def create_course(course: CourseCreate):
    course_read = CourseRead(**course.model_dump())
    courses[course_read.id] = course_read
    return course_read

@app.get("/courses", response_model=List[CourseRead])
def list_courses(
    code: Optional[str] = Query(None, description="Filter by course code"),
    title: Optional[str] = Query(None, description="Filter by course title"),
    department: Optional[str] = Query(None, description="Filter by department"),
    instructor: Optional[str] = Query(None, description="Filter by instructor"),
    semester: Optional[str] = Query(None, description="Filter by semester"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    min_credits: Optional[int] = Query(None, ge=1, le=6, description="Minimum credits"),
    max_credits: Optional[int] = Query(None, ge=1, le=6, description="Maximum credits"),
):
    results = list(courses.values())

    if code is not None:
        results = [c for c in results if c.code == code]
    if title is not None:
        results = [c for c in results if c.title.lower().find(title.lower()) != -1]
    if department is not None:
        results = [c for c in results if c.department.lower().find(department.lower()) != -1]
    if instructor is not None:
        results = [c for c in results if c.instructor and c.instructor.lower().find(instructor.lower()) != -1]
    if semester is not None:
        results = [c for c in results if c.semester.lower().find(semester.lower()) != -1]
    if is_active is not None:
        results = [c for c in results if c.is_active == is_active]
    if min_credits is not None:
        results = [c for c in results if c.credits >= min_credits]
    if max_credits is not None:
        results = [c for c in results if c.credits <= max_credits]

    return results

@app.get("/courses/{course_id}", response_model=CourseRead)
def get_course(course_id: UUID):
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    return courses[course_id]

@app.put("/courses/{course_id}", response_model=CourseRead)
def replace_course(course_id: UUID, course: CourseCreate):
    """Replace an entire course."""
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    courses[course_id] = CourseRead(id=course_id, **course.model_dump(exclude={"id"}))
    return courses[course_id]

@app.patch("/courses/{course_id}", response_model=CourseRead)
def update_course(course_id: UUID, update: CourseUpdate):
    """Partially update a course."""
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    stored = courses[course_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    courses[course_id] = CourseRead(**stored)
    return courses[course_id]

@app.delete("/courses/{course_id}", status_code=204)
def delete_course(course_id: UUID):
    """Delete a course."""
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    del courses[course_id]


# -----------------------------------------------------------------------------
# Enrollment endpoints
# -----------------------------------------------------------------------------

@app.post("/enrollments", response_model=EnrollmentRead, status_code=201)
def create_enrollment(enrollment: EnrollmentCreate):
    # Validate that student and course exist
    if not any(p.uni == enrollment.student_uni for p in persons.values()):
        raise HTTPException(status_code=400, detail="Student not found")
    if enrollment.course_id not in courses:
        raise HTTPException(status_code=400, detail="Course not found")
    
    # Check if course is active
    course = courses[enrollment.course_id]
    if not course.is_active:
        raise HTTPException(status_code=400, detail="Course is not active")
    
    # Check enrollment capacity
    if course.max_enrollment and course.current_enrollment >= course.max_enrollment:
        raise HTTPException(status_code=400, detail="Course enrollment is full")
    
    enrollment_read = EnrollmentRead(**enrollment.model_dump())
    enrollments[enrollment_read.id] = enrollment_read
    
    # Update course enrollment count
    course.current_enrollment += 1
    courses[enrollment.course_id] = course
    
    return enrollment_read

@app.get("/enrollments", response_model=List[EnrollmentRead])
def list_enrollments(
    student_uni: Optional[str] = Query(None, description="Filter by student UNI"),
    course_id: Optional[UUID] = Query(None, description="Filter by course ID"),
    status: Optional[EnrollmentStatus] = Query(None, description="Filter by enrollment status"),
    semester: Optional[str] = Query(None, description="Filter by semester (via course)"),
    department: Optional[str] = Query(None, description="Filter by department (via course)"),
):
    results = list(enrollments.values())

    if student_uni is not None:
        results = [e for e in results if e.student_uni == student_uni]
    if course_id is not None:
        results = [e for e in results if e.course_id == course_id]
    if status is not None:
        results = [e for e in results if e.status == status]
    if semester is not None:
        results = [e for e in results if e.course_id in courses and courses[e.course_id].semester.lower().find(semester.lower()) != -1]
    if department is not None:
        results = [e for e in results if e.course_id in courses and courses[e.course_id].department.lower().find(department.lower()) != -1]

    return results

@app.get("/enrollments/{enrollment_id}", response_model=EnrollmentRead)
def get_enrollment(enrollment_id: UUID):
    if enrollment_id not in enrollments:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollments[enrollment_id]

@app.put("/enrollments/{enrollment_id}", response_model=EnrollmentRead)
def replace_enrollment(enrollment_id: UUID, enrollment: EnrollmentCreate):
    """Replace an entire enrollment."""
    if enrollment_id not in enrollments:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Validate that course exists
    if enrollment.course_id not in courses:
        raise HTTPException(status_code=400, detail="Course not found")
    
    # Check if course is active
    course = courses[enrollment.course_id]
    if not course.is_active:
        raise HTTPException(status_code=400, detail="Course is not active")
    
    # Check enrollment capacity
    if course.max_enrollment and course.current_enrollment >= course.max_enrollment:
        raise HTTPException(status_code=400, detail="Course enrollment is full")
    
    enrollments[enrollment_id] = EnrollmentRead(id=enrollment_id, **enrollment.model_dump(exclude={"id"}))
    return enrollments[enrollment_id]

@app.patch("/enrollments/{enrollment_id}", response_model=EnrollmentRead)
def update_enrollment(enrollment_id: UUID, update: EnrollmentUpdate):
    """Partially update an enrollment."""
    if enrollment_id not in enrollments:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # If course_id is being updated, validate it exists
    if update.course_id is not None:
        if update.course_id not in courses:
            raise HTTPException(status_code=400, detail="Course not found")
    
    stored = enrollments[enrollment_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    enrollments[enrollment_id] = EnrollmentRead(**stored)
    return enrollments[enrollment_id]

@app.delete("/enrollments/{enrollment_id}", status_code=204)
def delete_enrollment(enrollment_id: UUID):
    """Delete an enrollment."""
    if enrollment_id not in enrollments:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Update course enrollment count
    enrollment = enrollments[enrollment_id]
    if enrollment.course_id in courses:
        course = courses[enrollment.course_id]
        course.current_enrollment = max(0, course.current_enrollment - 1)
        courses[enrollment.course_id] = course
    
    del enrollments[enrollment_id]

# -----------------------------------------------------------------------------
# Cross-resource endpoints
# -----------------------------------------------------------------------------

@app.get("/students/{student_id}/enrollments", response_model=List[EnrollmentRead])
def get_student_enrollments(student_uni: str):
    if not any(p.uni == student_uni for p in persons.values()):
        raise HTTPException(status_code=404, detail="Student not found")
    
    return [e for e in enrollments.values() if e.student_uni == student_uni]

@app.get("/courses/{course_id}/enrollments", response_model=List[EnrollmentRead])
def get_course_enrollments(course_id: UUID):
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return [e for e in enrollments.values() if e.course_id == course_id]

@app.get("/students/{student_id}/courses", response_model=List[CourseRead])
def get_student_courses(student_uni: str):
    if not any(p.uni == student_uni for p in persons.values()):
        raise HTTPException(status_code=404, detail="Student not found")
    
    student_enrollments = [e for e in enrollments.values() if e.student_uni == student_uni]
    course_ids = [e.course_id for e in student_enrollments]
    return [courses[cid] for cid in course_ids if cid in courses]


# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {
    "message": "Welcome to the Educational Microservices API. See /docs for OpenAPI UI.",
    "version": "0.2.0",
    "resources": {
        "persons": "/persons",
        "addresses": "/addresses", 
        "courses": "/courses",
        "enrollments": "/enrollments",
        "health": "/health"
    }
}

# -----------------------------------------------------------------------------
# Entrypoint for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.database import get_session
from app.models.student import Student
from app.auth import verify_token
 
router = APIRouter(prefix="/students",tags=["Students"])
security = HTTPBearer()
 
 
def authenticate(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
 
    payload = verify_token(token)
 
    if not payload:
        raise HTTPException(status_code=401,detail="Invalid or expired token")
    return payload
 
 

# 1. GET ALL STUDENTS
@router.get("/")
def students(session: Session = Depends(get_session)):
    return session.exec(select(Student)).all()
 
# 2. CREATE STUDENT
@router.post("/")
def add_student(student: Student,credentials: HTTPAuthorizationCredentials = Depends(security),session: Session = Depends(get_session)):
 
    authenticate(credentials)
    session.add(student)
    session.commit()
    session.refresh(student)
    return student
 
# 3. GET STUDENT BY ID
@router.get("/{student_id}")
def student_by_id(student_id: str,session: Session = Depends(get_session)):
 
    student = session.exec(select(Student).where(Student.student_id == student_id)).first()
 
    if not student:
        raise HTTPException(status_code=404,detail="Student not found")
    return student


# 4. UPDATE STUDENT
@router.put("/{student_id}")
def update(student_id: str,student_data: Student,credentials: HTTPAuthorizationCredentials = Depends(security),session: Session = Depends(get_session)):
 
    authenticate(credentials)
 
    student = session.exec(select(Student).where(Student.student_id == student_id)).first()
 
    if not student:
        raise HTTPException(status_code=404,detail="Student not found")
 
    student.name = student_data.name
    student.age = student_data.age
    student.city = student_data.city
    student.stream = student_data.stream
 
    session.add(student)
    session.commit()
    session.refresh(student)
 
    return student
 
# 5. DELETE STUDENT
 
@router.delete("/{student_id}")
def delete(student_id: str,credentials: HTTPAuthorizationCredentials = Depends(security),session: Session = Depends(get_session)):
 
    authenticate(credentials)
 
    student = session.exec(select(Student).where(Student.student_id == student_id)).first()
 
    if not student:
        raise HTTPException(status_code=404,detail="Student not found")
 
    session.delete(student)
    session.commit()
 
    return {"message": "Student deleted successfully"}
 
 # 6. GET STUDENTS BY CITY
 
@router.get("/city/{city}")
def students_by_city(city: str,session: Session = Depends(get_session)):
 
    return session.exec(select(Student).where(Student.city == city)).all()
 
 
# 7. GET STUDENTS BY STREAM
 
@router.get("/stream/{stream}")
def students_by_stream(stream: str,session: Session = Depends(get_session)):
 
    return session.exec(select(Student).where(Student.stream == stream)).all()
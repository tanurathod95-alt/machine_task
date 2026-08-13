from fastapi import (APIRouter,Depends,HTTPException,UploadFile,File,status)
from sqlmodel import Session, select
from app.database import get_session
from app.models.student import Student
from app.auth import authenticate
from app.seed.seed_runner import seed_students
import pandas as pd
import io


router = APIRouter(prefix="/students",tags=["Students"])
# 1. GET ALL STUDENTS


@router.get("/")
def get_all_students(session: Session = Depends(get_session)):

    students = session.exec(select(Student)).all()

    if len(students) == 0:
        seed_students()

        students = session.exec(select(Student)).all()

    return students
# 2. CREATE STUDENT
@router.post("/",status_code=status.HTTP_201_CREATED,dependencies=[Depends(authenticate)])
def add_student(
    student: Student,
    session: Session = Depends(get_session)
):

   
    existing_student = session.exec(select(Student).where(Student.student_id == student.student_id)).first()

    if existing_student:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Student ID already exists")

    session.add(student)
    session.commit()
    session.refresh(student)

    return {"message": "Student added successfully","student": student}
# 3. UPLOAD EXCEL
@router.post("/upload-excel",dependencies=[Depends(authenticate)])
async def upload_excel(file: UploadFile = File(...),session: Session = Depends(get_session)):

    if not file.filename:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="File is required")

    if not file.filename.lower().endswith((".xlsx", ".xls")):

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Only Excel files are allowed")
    try:

        contents = await file.read()

        df = pd.read_excel(io.BytesIO(contents))

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to read Excel file: {str(e)}"
        )

    # Required Excel columns
    required_columns = [
        "student_id",
        "first_name",
        "last_name",
        "class_name",
        "section",
        "stream",
        "city",
        "attendance"
    ]

    # Check missing columns
    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Required columns are missing",
                "missing_columns": missing_columns
            }
        )

    inserted_count = 0
    skipped_count = 0
    for _, row in df.iterrows():

        student_id = str(
            row["student_id"]
        ).strip()

        
        if not student_id or student_id == "nan":

            skipped_count += 1
            continue

        
        existing_student = session.exec(
            select(Student).where(
                Student.student_id == student_id
            )
        ).first()

        if existing_student:

            skipped_count += 1
            continue

        
        student = Student(
            student_id=student_id,

            first_name=str(
                row["first_name"]
            ).strip(),

            last_name=str(
                row["last_name"]
            ).strip(),

            class_name=str(
                row["class_name"]
            ).strip(),

            section=str(
                row["section"]
            ).strip(),

            stream=str(
                row["stream"]
            ).strip(),

            city=str(
                row["city"]
            ).strip(),

            attendance=float(
                row["attendance"]
            )
        )

        session.add(student)

        inserted_count += 1

    
    session.commit()

    return {
        "message": "Excel data uploaded successfully",
        "records_inserted": inserted_count,
        "records_skipped": skipped_count
    }
# 4. GET STUDENTS BY CITY


@router.get("/city/{city}")
def get_students_by_city(city: str,session: Session = Depends(get_session)):

    students = session.exec(select(Student).where(Student.city == city)).all()

    return students
# 5. GET STUDENTS BY STREAM
@router.get("/stream/{stream}")
def get_students_by_stream(stream: str,session: Session = Depends(get_session)):
    students = session.exec(select(Student).where(Student.stream == stream)).all()
    return students


# 6. GET STUDENT BY ID
@router.get("/{student_id}")
def get_student_by_id(student_id: str,session: Session = Depends(get_session)):
    student = session.exec(select(Student).where(Student.student_id == student_id)).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Student not found")
    return student

# 7. UPDATE STUDENT
@router.put("/{student_id}",dependencies=[Depends(authenticate)])
def update_student(student_id: str,student_data: Student,session: Session = Depends(get_session)):
    student = session.exec(select(Student).where(Student.student_id == student_id)).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Student not found")
    # Update fields
    student.first_name = student_data.first_name
    student.last_name = student_data.last_name
    student.class_name = student_data.class_name
    student.section = student_data.section
    student.stream = student_data.stream
    student.city = student_data.city
    student.attendance = student_data.attendance

    session.add(student)
    session.commit()
    session.refresh(student)
    return {
        "message": "Student updated successfully",
        "student": student
    }


# 8. DELETE STUDENT
@router.delete("/{student_id}",dependencies=[Depends(authenticate)])
def delete_student(student_id: str,session: Session = Depends(get_session)):
    student = session.exec(select(Student).where(Student.student_id == student_id)).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Student not found")
    session.delete(student)
    session.commit()
    return {
        "message": "Student deleted successfully",
        "student_id": student_id
    }
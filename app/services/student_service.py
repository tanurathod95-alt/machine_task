from sqlmodel import Session, select
from app.models.student import Student


def get_all_students(session: Session):
    statement = select(Student)
    return session.exec(statement).all()


def get_student(session: Session,student_id: str):
    statement = select(Student).where(Student.student_id == student_id)
    return session.exec(statement).first()


def create_student(session: Session,student: Student):
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


def update_student(session: Session,student_id: str,data: dict):
    student = get_student(session,student_id)

    if not student:
        return None

    for key, value in data.items():
        if value is not None:
            setattr(student,key,value)
        session.add(student)
        session.commit()
        session.refresh(student)
        return student


def delete_student(session: Session,student_id: str):
    student = get_student(session,student_id)
    if not student:
        return False
    session.delete(student)
    session.commit()
    return True


def get_students_by_city(session: Session,city: str):
    statement = select(Student).where(Student.city == city)
    return session.exec(statement).all()


def get_students_by_stream(session: Session,stream: str):
    statement = select(Student).where(Student.stream == stream)
    return session.exec(statement).all()
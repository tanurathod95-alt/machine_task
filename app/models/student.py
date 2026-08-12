from sqlmodel import SQLModel, Field


class Student(SQLModel, table=True):

    id: int | None = Field(default=None, primary_key=True)
    student_id:str=Field(unique=True,index=True)
    first_name: str
    last_name: str
    class_name: str
    section: str
    stream: str
    city: str
    attendance: float
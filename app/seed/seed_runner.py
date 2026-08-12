import os
import pandas as pd
from pathlib import Path
from sqlmodel import Session, select
from app.database import engine, create_db_and_tables
from app.models.student import Student


BASE_DIR = Path(__file__).resolve().parent

EXCEL_FILE = BASE_DIR / "Student_Records.xlsx"


def seed_students():
    print("Starting student data seeding...")
   
    create_db_and_tables()

    print(f"Looking for Excel file:")
    print(EXCEL_FILE)

    if not EXCEL_FILE.exists():
        print("Excel file not found!")
        print(f"Expected location: {EXCEL_FILE}")
        return

    print("Excel file found!")

    xl = pd.ExcelFile(EXCEL_FILE)
    print(f"Available sheets: {xl.sheet_names}")

    df = pd.read_excel(EXCEL_FILE, sheet_name=0)

    print(f"Excel records found: {len(df)}")
    print(f"Columns found: {list(df.columns)}")

    inserted_count = 0
    skipped_count = 0

    with Session(engine) as session:

        for _, row in df.iterrows():

            student_id = str(row["Student ID"]).strip()

            existing_student = session.exec(select(Student).where(Student.student_id == student_id)).first()

            if existing_student:
                skipped_count += 1
                continue

            student = Student(
                student_id=student_id,
                first_name=str(row["First Name"]).strip(),
                last_name=str(row["Last Name"]).strip(),
                class_name=str(row["Class"]).strip(),
                section=str(row["Section"]).strip(),
                stream=str(row["Stream"]).strip(),
                city=str(row["City"]).strip(),
                attendance=float(row["Attendance (%)"])
            )

            session.add(student)
            inserted_count += 1

        session.commit()

    print(f"Students inserted: {inserted_count}")
    print(f"Students skipped: {skipped_count}")
    print("Student data inserted successfully!")


if __name__ == "__main__":
    seed_students()
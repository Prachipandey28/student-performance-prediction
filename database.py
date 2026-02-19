"""
database.py - EduSense v5 - SQLite Student Database
Columns: 30 total (student_id, name, email, phone, gender, age,
         domain, branch, subjects, internet_access, extra_support,
         attendance, study_hours, screen_time, prev_cgpa,
         current_sem_cgpa, assignments, midterm_score, sleep_hours,
         absences, activities, stress_level,
         final_score, cgpa, grade, pass_fail, at_risk,
         created_at, updated_at)
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime


class StudentDatabase:
    def __init__(self, db_path="data/students.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id       INTEGER PRIMARY KEY,
                name             TEXT    NOT NULL,
                email            TEXT,
                phone            TEXT,
                gender           TEXT    NOT NULL,
                age              INTEGER NOT NULL,
                domain           TEXT    NOT NULL,
                branch           TEXT    NOT NULL,
                subjects         TEXT    NOT NULL,
                internet_access  TEXT    NOT NULL,
                extra_support    TEXT    NOT NULL,
                attendance       REAL    NOT NULL,
                study_hours      REAL    NOT NULL,
                screen_time      REAL    NOT NULL,
                prev_cgpa        REAL    NOT NULL,
                current_sem_cgpa REAL    NOT NULL,
                assignments      REAL    NOT NULL,
                midterm_score    REAL    NOT NULL,
                sleep_hours      REAL    NOT NULL,
                absences         INTEGER NOT NULL,
                activities       TEXT    NOT NULL,
                stress_level     TEXT    NOT NULL,
                final_score      REAL,
                cgpa             REAL,
                grade            TEXT,
                pass_fail        TEXT,
                at_risk          INTEGER,
                created_at       TEXT,
                updated_at       TEXT
            )
        """)
        self.conn.commit()

    # ── helpers ──────────────────────────────────────────
    @staticmethod
    def score_to_cgpa(score):
        if score >= 90: return 10.0
        if score >= 80: return 9.0
        if score >= 70: return 8.0
        if score >= 60: return 7.0
        if score >= 50: return 6.0
        if score >= 40: return 5.0
        return 4.0

    @staticmethod
    def cgpa_to_grade(cgpa):
        if cgpa >= 9.0: return "O"
        if cgpa >= 8.0: return "A+"
        if cgpa >= 7.0: return "A"
        if cgpa >= 6.0: return "B+"
        if cgpa >= 5.0: return "B"
        return "F"

    def _calculate(self, data):
        stress = {"Low": 0, "Medium": -3, "High": -7}
        screen_pen = max(0, (float(data["screen_time"]) - 4) * 1.5)

        score = (
            0.22 * float(data["attendance"]) +
            0.20 * float(data["midterm_score"]) +
            0.18 * float(data["prev_cgpa"]) * 10 +
            0.15 * float(data["assignments"]) +
            0.10 * float(data["study_hours"]) * 5 +
            0.05 * float(data["sleep_hours"]) * 5 +
            stress.get(data["stress_level"], 0) -
            screen_pen -
            int(data["absences"]) * 0.5 +
            (3 if data["internet_access"] == "Yes" else 0) +
            (2 if data["extra_support"] == "Yes" else 0)
        )
        score = round(max(0.0, min(100.0, score)), 2)
        cgpa  = self.score_to_cgpa(score)
        grade = self.cgpa_to_grade(cgpa)
        data["final_score"] = score
        data["cgpa"]        = cgpa
        data["grade"]       = grade
        data["pass_fail"]   = "Pass" if grade != "F" else "Fail"
        data["at_risk"]     = 1 if cgpa < 5.0 else 0
        return data

    # ── CRUD ─────────────────────────────────────────────
    def add_student(self, d):
        d = self._calculate(d)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        d["created_at"] = now
        d["updated_at"] = now
        try:
            self.cursor.execute(
                """INSERT INTO students VALUES (
                    :student_id, :name, :email, :phone,
                    :gender, :age, :domain, :branch, :subjects,
                    :internet_access, :extra_support,
                    :attendance, :study_hours, :screen_time,
                    :prev_cgpa, :current_sem_cgpa,
                    :assignments, :midterm_score, :sleep_hours,
                    :absences, :activities, :stress_level,
                    :final_score, :cgpa, :grade, :pass_fail, :at_risk,
                    :created_at, :updated_at
                )""",
                d,
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_student(self, student_id, d):
        d = self._calculate(d)
        d["updated_at"]  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        d["student_id"]  = student_id
        self.cursor.execute(
            """UPDATE students SET
                name=:name, email=:email, phone=:phone,
                gender=:gender, age=:age,
                domain=:domain, branch=:branch, subjects=:subjects,
                internet_access=:internet_access, extra_support=:extra_support,
                attendance=:attendance, study_hours=:study_hours,
                screen_time=:screen_time,
                prev_cgpa=:prev_cgpa, current_sem_cgpa=:current_sem_cgpa,
                assignments=:assignments, midterm_score=:midterm_score,
                sleep_hours=:sleep_hours, absences=:absences,
                activities=:activities, stress_level=:stress_level,
                final_score=:final_score, cgpa=:cgpa,
                grade=:grade, pass_fail=:pass_fail, at_risk=:at_risk,
                updated_at=:updated_at
            WHERE student_id=:student_id""",
            d,
        )
        self.conn.commit()

    def delete_student(self, student_id):
        self.cursor.execute("DELETE FROM students WHERE student_id=?", (int(student_id),))
        self.conn.commit()

    def get_student(self, student_id):
        self.cursor.execute("SELECT * FROM students WHERE student_id=?", (int(student_id),))
        row = self.cursor.fetchone()
        if row:
            cols = [d[0] for d in self.cursor.description]
            return dict(zip(cols, row))
        return None

    def get_dataframe(self):
        return pd.read_sql_query("SELECT * FROM students ORDER BY student_id", self.conn)

    def exists(self, student_id):
        self.cursor.execute("SELECT 1 FROM students WHERE student_id=?", (int(student_id),))
        return self.cursor.fetchone() is not None

    def close(self):
        self.conn.close()
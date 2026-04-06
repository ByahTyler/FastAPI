from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, Boolean, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from enum import Enum
import uuid
import time
import random
import logging

# Database setup
DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
MAX_RETRIES = 2

class Operation(str, Enum):
    add = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"

# Database model
class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    completed = Column(Boolean, default=False)
    job_id = Column(String)
    status = Column(String, default="pending")
    number = Column(Integer)
    operand = Column(Integer)
    operation = Column(String)
    result = Column(Integer)

# Create tables
Base.metadata.create_all(bind=engine)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Pydantic model
class Task(BaseModel):
    title: str
    number: int = Field(..., gt=0)
    operand: int = Field(..., gt=0)
    operation: Operation

app = FastAPI()

# In-memory job store
jobs = {}

# DB session context manager
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate(number: int, operand: int, operation: Operation) -> float:
    if operation == Operation.add:
        return number + operand
    elif operation == Operation.subtract:
        return number - operand
    elif operation == Operation.multiply:
        return number * operand
    elif operation == Operation.divide:
        if operand == 0:
            raise ValueError("Cannot divide by zero")
        return number / operand

# Background job processor
def process_job(job_id: str, task_id: str):
    job = jobs[job_id]
    job["status"] = "running"

    for attempt in range(1, MAX_RETRIES + 2):
        time.sleep(3)

        with get_db() as db:
            task = db.query(TaskDB).filter(TaskDB.id == task_id).first()

            if not task:
                logging.error(f"Task {task_id} not found for job {job_id}")
                job["status"] = "failed"
                return

            if random.choice([True, False]):  # simulated failure
                logging.warning(f"Job {job_id} failed (attempt {attempt})")
                job["retries"] = attempt
                job["status"] = "retrying" if attempt <= MAX_RETRIES else "failed"
                if attempt > MAX_RETRIES:
                    task.status = "failed"
                    db.commit()
                    return
                continue

            # Success
            try:
                result = calculate(task.number, task.operand, task.operation)
            except ValueError as e:
                logging.error(f"Job {job_id} calculation error: {e}")
                job["status"] = "failed"
                task.status = "failed"
                db.commit()
                return

            task.result = result
            task.status = "completed"
            task.completed = True
            job["status"] = "completed"
            logging.info(f"Job {job_id} completed: {task.number} {task.operation} {task.operand} = {result}")
            db.commit()
            return


# Create task (triggers job)
@app.post("/tasks")
def create_task(task: Task, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    with get_db() as db:
        db_task = TaskDB(
            id=task_id,
            title=task.title,
            completed=False,
            job_id=job_id,
            status="pending",
            number=task.number,
            operand=task.operand,
            operation=task.operation,
            result=None
        )
        db.add(db_task)
        db.commit()

    jobs[job_id] = {"status": "pending", "retries": 0}
    background_tasks.add_task(process_job, job_id, task_id)

    return {"task_id": task_id, "job_id": job_id, "status": "pending"}


# Get all tasks
@app.get("/tasks")
def get_tasks(status: str = None, min_number: int = None):
    with get_db() as db:
        query = db.query(TaskDB)
        if status:
            query = query.filter(TaskDB.status == status)
        if min_number is not None:
            query = query.filter(TaskDB.number >= min_number)
        return query.all()


# Get single task
@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    with get_db() as db:
        task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# Delete task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    with get_db() as db:
        task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        db.delete(task)
        db.commit()
    return {"message": "Task deleted"}


# Get job status
@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]
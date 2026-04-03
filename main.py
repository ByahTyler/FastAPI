from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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

# Database model
class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    completed = Column(Boolean, default=False)
    job_id = Column(String)
    status = Column(String, default="pending")

    number = Column(Integer)
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
    number: int

app = FastAPI()

# In-memory job store
jobs = {}

# Background job processor
def process_job(job_id: str, task_id: str):
    job = jobs[job_id]

    logging.info(f"Job {job_id} started for task {task_id}")

    job["status"] = "running"
    time.sleep(3)

    db = SessionLocal()
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()

    if not task:
        logging.error(f"Task {task_id} not found for job {job_id}")
        job["status"] = "failed"
        db.close()
        return

    # Simulate failure
    if random.choice([True, False]):
        job["retries"] += 1
        logging.warning(f"Job {job_id} failed (attempt {job['retries']})")

        if job["retries"] <= MAX_RETRIES:
            job["status"] = "retrying"
            logging.info(f"Retrying job {job_id}")

            db.close()
            process_job(job_id, task_id)
            return
        else:
            job["status"] = "failed"
            task.status = "failed"
            logging.error(f"Job {job_id} permanently failed after retries")
    
    else:
        # Processing data
        result = task.number * 10

        task.result = result
        task.status = "completed"
        task.completed = True

        job["status"] = "completed"

        logging.info(f"Job {job_id} completed: {task.number} * 10 = {result}")

    db.commit()
    db.close()

# Create task (triggers job)
@app.post("/tasks")
def create_task(task: Task, background_tasks: BackgroundTasks):
    db = SessionLocal()

    task_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    db_task = TaskDB(
        id=task_id,
        title=task.title,
        completed=False,
        job_id=job_id,
        status="pending",
        number=task.number,
        result=None
    )

    db.add(db_task)
    db.commit()

    # Create job
    jobs[job_id] = {
        "status": "pending",
        "retries": 0
    }

    # Run job in background
    background_tasks.add_task(process_job, job_id, task_id)

    db.close()

    return {
        "task_id": task_id,
        "job_id": job_id,
        "status": "pending"
    }

# Get all tasks
@app.get("/tasks")
def get_tasks(status: str = None, min_number: int = None):
    db = SessionLocal()
    query = db.query(TaskDB)

    if status:
        query = query.filter(TaskDB.status == status)

    if min_number is not None:
        query = query.filter(TaskDB.number >= min_number)

    tasks = query.all()
    db.close()

    return tasks

# Get single task
@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    db = SessionLocal()
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    db.close()

    if task:
        return task

    raise HTTPException(status_code=404, detail="Task not found")

# Delete task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    db = SessionLocal()
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()

    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    db.close()

    return {"message": "Task deleted"}

# Get job status
@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]
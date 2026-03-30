from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Database model
class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    completed = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# Pydantic model
class Task(BaseModel):
    title: str
    completed: bool = False

# Create task
@app.post("/tasks")
def create_task(task: Task):
    db = SessionLocal()
    db_task = TaskDB(
        id=str(uuid.uuid4()),
        title=task.title,
        completed=task.completed
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    db.close()
    return db_task

# Get all tasks
@app.get("/tasks")
def get_tasks():
    db = SessionLocal()
    tasks = db.query(TaskDB).all()
    db.close()
    return tasks

# Get one task
@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    db = SessionLocal()
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    db.close()
    if task:
        return task
    return {"error": "Task not found"}

# Delete task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    db = SessionLocal()
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        db.close()
        return {"message": "Task deleted"}
    db.close()
    return {"error": "Task not found"}

@app.put("/tasks/{task_id}")
def update_task(task_id: str, updated_task: Task):
    db = SessionLocal()
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()

    if task:
        task.title = updated_task.title
        task.completed = updated_task.completed
        db.commit()
        db.refresh(task)
        db.close()
        return task

    db.close()
    return {"error": "Task not found"}
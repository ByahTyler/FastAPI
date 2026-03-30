from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uuid

app = FastAPI()

# Data model
class Task(BaseModel):
    id: str = None
    title: str
    completed: bool = False

# Create a list
tasks: List[Task] = []

# Root
@app.get("/")
def read_root():
    return {"message": "API is running"}

# Creates a task
@app.post("/tasks")
def create_task(task: Task):
    task.id = str(uuid.uuid4())
    tasks.append(task)
    return task

# Returns all tasks
@app.get("/tasks")
def get_tasks():
    return tasks

# Get a single task
@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    for task in tasks:
        if task.id == task_id:
            return task
    return {"error": "Task not found"}

# Deletes a task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            return tasks.pop(i)
    return {"error": "Task not found"}
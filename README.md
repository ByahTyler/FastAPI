# Async Task Processing API

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green)
![SQLAlchemy](https://img.shields.io/badge/Database-SQLAlchemy-orange)
![Status](https://img.shields.io/badge/Project-Active-success)

---

## Overview

This project is a backend system built with FastAPI that simulates real-world asynchronous job processing. Users can create tasks that trigger background jobs, which process data, handle failures with retries, and store results in a database.

The system demonstrates key backend engineering concepts such as API design, background processing, retry logic, logging, and database interaction.

---

## Features

- RESTful API for task management  
- Background job processing using FastAPI BackgroundTasks  
- Retry logic for failed jobs  
- Structured logging for observability  
- SQLite database for persistence  
- Input validation using Pydantic  
- Dynamic query filtering for retrieving tasks  
- Asynchronous processing with real computation (number × 10)  

---

## Tech Stack

- Python  
- FastAPI  
- SQLAlchemy  
- SQLite  
- Uvicorn  

---

## How It Works

1. A user sends a request to create a task  
2. The API stores the task in the database  
3. A background job is triggered  
4. The job processes the task (multiplies a number by 10)  
5. If the job fails, it retries up to a defined limit  
6. The task is updated with the result and status  
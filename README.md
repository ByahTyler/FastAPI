# Async Task Processing API

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)

## Overview
Backend API built with FastAPI that processes tasks asynchronously. Tasks trigger background jobs that perform calculations, retry on failure, and store results in PostgreSQL.

## Features
- REST API
- Background jobs with retries
- PostgreSQL database
- Dockerized services
- Docker Compose orchestration

## Tech Stack
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker
- Docker Compose

## Run with Docker

Start:
docker compose up --build

Run in background:
docker compose up -d

Stop:
docker compose down

## API

Docs:
http://localhost:8000/docs

Example request:
{
  "title": "test",
  "number": 10,
  "operand": 5,
  "operation": "multiply"
}

## How It Works
1. Create task via API
2. Task stored in PostgreSQL
3. Background job runs
4. Retries on failure
5. Result saved
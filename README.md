# Lyftr Backend Assignment

This repository contains a production-ready backend service built as part of the Lyftr Backend Assignment.

The service handles secure webhook ingestion, message storage, querying, analytics, and structured logging. It is fully containerized using Docker and can be run with a single command.

---

## Overview

The backend exposes APIs to:
- Securely ingest webhook events using HMAC signature verification
- Ensure idempotent message processing
- Store messages in a SQLite database
- Query stored messages with filters, pagination, and search
- Provide aggregated message statistics
- Emit structured JSON logs for observability

The application is designed to be simple, reliable, and easy to run locally or in a containerized environment.

---

## Tech Stack

- **Python 3.11**
- **FastAPI**
- **SQLite**
- **Docker & Docker Compose**

---

## Project Structure
backend-assignment/
├── app/
│ ├── main.py
│ ├── models.py
│ ├── schemas.py
│ ├── config.py
│ ├── security.py
│ └── logging_utils.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── Makefile
└── README.md


---

## ⚙️ Prerequisites

- Docker
- Docker Compose

No local Python setup is required when running via Docker.

---

## ▶️ Running the Application

### Start the service
From the project root:

```bash
docker compose up


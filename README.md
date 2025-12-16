Safe Python Code Executor - README & Security Report
README

Title: Safe Python Code Executor Using Docker
Author: Tarun Patil

1. Project Overview

This project is a Safe Code Executor that allows users to submit Python code through an API or a simple web UI.
The code is executed inside a Docker container to provide safety, isolation, and resource control.

This project was built for learning purposes to understand:

- How to run untrusted code inside containers
- Basic Docker security features
- API development
- Resource limits (timeout, memory, CPU, no network)
- Limits of Docker as a security boundary

 2. Features Implemented

API Endpoint

POST /run

Request body:
{ "code": "print(2 + 2)" }

Successful response:
{ "success": true, "output": "4\n" }

Error response:
{ "success": false, "error": "Execution timed out after 10 seconds." }

 Basic Safety (As Required in Task)

Attack Type | Example Code | Protection Used
- Infinite Loop | while True: pass | Timeout = 10 seconds
- High Memory | "a" * 1000000000 | Docker memory limit = 128 MB
- Network Access | requests.get() | --network none
- Long Code | > 5000 characters | Code length validation

 Docker Security Flags Used

docker run --rm \
  --network none \
  --memory 128m \
  --cpus 0.5 \
  --pids-limit 64 \
  -v <temp_dir>:/app \
  -w /app \
  python:3.11-slim python script.py

For security experiment:
--read-only
-v <temp_dir>:/app:ro

Web UI Included

A simple HTML interface with:
- Textarea for code input
- Run button
- Output/Error display

3. How to Install and Run

Step 1 — Install dependencies
pip install -r requirements.txt

Step 2 — Start Docker Desktop

Step 3 — Pull Python Docker image
docker pull python:3.11-slim

Step 4 — Run the Flask App
python app.py

Step 5 — Open the UI
http://127.0.0.1:5000

 4. How the Code Execution Works

- API receives the Python code
- Writes the code to script.py
- Executes inside Docker container
- Returns output/error

 5. What I Learned

- Safe execution using Docker
- Network blocking using --network none
- Resource limits importance
- Why untrusted code is risky
- Docker isolation limitations
- Flask API development
- Error handling
- Building simple frontend UI

 6. File Structure

safe-code-executor/
│── app.py
│── requirements.txt
└── templates/
    └── index.html


Security Report


 1. Objective
Understand:
- What Docker containers can access
- How to secure execution environments
- Effects of --read-only, --memory, --network none

2. Experiment 1 — Reading /etc/passwd

Code:
with open("/etc/passwd") as f:
    print(f.read())

Result:
Worked. Container printed file contents.

Reason:
Docker includes its own Linux filesystem. /etc/passwd is available inside.

 3. Experiment 2 — Writing to /tmp/test.txt (Without Read-Only Mode)

Code:
with open("/tmp/test.txt", "w") as f:
    f.write("hacked!")
print("Write completed")

Result:
Worked.

Reason:
Container filesystem is writable by default.

 4. Experiment 3 — Write WITH --read-only enabled

Same Code:
with open("/tmp/test.txt", "w") as f:
    f.write("hacked!")

Result:
Failed. Error: [Errno 30] Read-only file system

Reason:
--read-only + :ro mount prevents file modifications.

 5. Additional Safety Tests

Infinite Loop:
Stopped after 10 seconds → timeout works.

Memory Attack:
Killed due to 128 MB memory cap.

Network Access:
Blocked due to --network none.

 6. What I Learned About Docker Security

- Docker provides isolation but not total security.
- File reads are allowed unless restricted.
- Write protection requires --read-only.
- Resource limits (memory, CPU, PID) protect host machine.
- Network isolation prevents data exfiltration.
- Need multiple layers of security for untrusted code.

 Final Summary

Docker Protects Against:
- High memory usage
- Infinite loops
- Network attacks
- Fork bombs
- File changes when read-only mode is used

Docker Does NOT Protect Against:
- Reading internal container files
- Writing to container filesystem (without read-only)



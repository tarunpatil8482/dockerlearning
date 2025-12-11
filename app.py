import os
import tempfile
import subprocess
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


def run_code_in_docker(code: str):
    """
    Runs the given Python code inside a Docker container (python:3.11-slim)
    with basic security limits: time, memory, no network, etc.
    Returns (success: bool, output: str).
    """

    # 1) Limit code size to 5000 characters
    if len(code) > 5000:
        return False, "Code too long. Maximum length is 5000 characters."

    # 2) Create temporary directory and write script.py there
    temp_dir = tempfile.mkdtemp()
    script_path = os.path.join(temp_dir, "script.py")

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)

    # 3) Prepare docker run command
    docker_cmd = [
        "docker", "run",
        "--rm",
        "--read-only",        # <--- read-only filesystem
        "--network", "none",
        "--memory", "128m",
        "--cpus", "0.5",
        "--pids-limit", "64",
        "-v", f"{temp_dir}:/app:ro",  # read-only mount
        "-w", "/app",
        "python:3.11-slim",
        "python", "script.py",
    ]

    try:
        # 4) Run docker, stop after 10 seconds
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
    except subprocess.TimeoutExpired:
        return False, "Execution timed out after 10 seconds."
    except FileNotFoundError:
        return False, "Docker is not installed or not found in PATH."
    except Exception as e:
        return False, f"Unexpected error while running code: {e}"

    # 5) Check if container exited with error
    if result.returncode != 0:
        error_output = result.stderr.strip() or result.stdout.strip()
        if not error_output:
            # likely resource limit
            error_output = "Execution failed, probably due to resource limits (memory/CPU/filesystem)."
        return False, error_output

    # 6) Success → return stdout
    return True, result.stdout


@app.route("/", methods=["GET"])
def index():
    # Show HTML UI
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run_code():
    """
    POST /run
    Body: { "code": "print(2 + 2)" }
    """
    data = request.get_json(silent=True)

    if not data or "code" not in data:
        return jsonify({
            "success": False,
            "error": "Please send JSON with a 'code' field."
        }), 400

    code = data["code"]

    success, output = run_code_in_docker(code)

    if success:
        return jsonify({
            "success": True,
            "output": output
        })
    else:
        return jsonify({
            "success": False,
            "error": output
        }), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

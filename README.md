## Developer Instructions

**Recommended Python:** Use Python 3.11 for development work and local execution. The `server/requirements.txt` file contains versions (including `SQLAlchemy==2.0.25`) that may be incompatible with Python 3.14.

- **Project requirements:** found in `server/requirements.txt`.

**Creating and using a virtual environment (PowerShell)**:

```powershell
# Navigate to the server directory
cd .\server

# If you have Python 3.11 installed as a specific instance:
& C:/Users/Fisher/AppData/Local/Programs/Python/Python311/python.exe -m venv .venv

# Alternatively, when using the py launcher:
py -3.11 -m venv .venv

# Allow running scripts in this session (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# Activate the environment
.\.venv\Scripts\Activate.ps1

# Update pip and install dependencies
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Running the Flask server (options)**:

- Preferred (Flask CLI) — run from the `server` directory with activated venv:

```powershell
flask run --host=0.0.0.0

# Or explicitly set the application factory
$env:FLASK_APP = "main:create_app"
flask run --host=0.0.0.0
```

- Alternatively run directly:

```powershell
python main.py
```

**Notes and troubleshooting**:

- If you get an error "Failed to find Flask application or factory in module 'app'", make sure you're running the command from the `server` directory (so that `main.py` is importable), or set `FLASK_APP` to `main:create_app` as above.
- If `pip install -r requirements.txt` fails when compiling native modules (e.g., face recognition libraries), comment out optional items in `server/requirements.txt` and run the installation again.
- To check installed versions inside venv:

```powershell
python -c "import sqlalchemy, flask_sqlalchemy; print('SQLAlchemy', sqlalchemy.__version__); print('Flask_SQLAlchemy', flask_sqlalchemy.__version__)"
```
"""Application package initializer.

This module re-exports the `create_app` factory from `main.py` so the
Flask CLI can discover the application when you run `flask run` from the
`server/` directory (the default FLASK_APP is `app`).
"""

try:
	from main import create_app
except Exception:
	def create_app(*args, **kwargs):
		raise RuntimeError(
			"Could not import `create_app` from `main.py`. "
			"Run the Flask CLI from the `server/` folder or use `flask --app main:create_app run`."
		)

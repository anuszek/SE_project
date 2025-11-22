"""Application package initializer.

This module re-exports the `create_app` factory from `main.py` so the
Flask CLI can discover the application when you run `flask run` from the
`server/` directory (the default FLASK_APP is `app`).
"""

try:
	# When running inside the `server` folder, `main.py` is importable
	# as the top-level module `main`.
	from main import create_app  # re-export the factory
except Exception:
	# Provide a helpful fallback if import fails at runtime.
	def create_app(*args, **kwargs):
		raise RuntimeError(
			"Could not import `create_app` from `main.py`. "
			"Run the Flask CLI from the `server/` folder or use `flask --app main:create_app run`."
		)

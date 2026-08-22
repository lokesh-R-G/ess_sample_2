import os
# Extend this package's __path__ to include the backend/app directory so that
# imports like `import app.permission.engine.seed_permissions` resolve correctly.
backend_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))
if backend_app_path not in __path__:
    __path__.append(backend_app_path)

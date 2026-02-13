### Development Notes – Python Version & PyCharm

During frontend integration, the PyQueue backend was restructured into a monorepo (`pyqueue_backend` and `pyqueue_frontend`) and treated as a proper Python package with explicit source roots. At this point, unresolved import warnings appeared in PyCharm for third-party libraries such as `fastapi` and `pydantic`, despite the backend running correctly from the command line.

The root cause was interpreter ambiguity. PyCharm’s FastAPI project template had initially auto-selected Python 3.13 (the newest version installed on the system). While this worked during early development, Python 3.13 is not yet fully supported by FastAPI/Pydantic tooling or PyCharm’s type indexer. Once the project gained real structure, PyCharm revalidated the interpreter and marked it as invalid, preventing proper import resolution.

The issue was resolved by explicitly installing and pinning **Python 3.12**, creating a virtual environment using that version, and configuring PyCharm to use the backend’s venv interpreter:

```
pyqueue_backend\.venv\Scripts\python.exe
```

After invalidating PyCharm’s caches and allowing the project to reindex, all imports resolved correctly. This reinforced the importance of explicitly managing Python versions once a project moves beyond a simple script layout and into a structured backend application.

## 2. Ultra-Condensed Footnote (Corny LinkedIn Post)

> **Note:** The PyQueue backend is pinned to Python 3.12. During development, Python 3.13 (auto-selected by PyCharm’s FastAPI template) caused unresolved import issues once the project was structured as a monorepo. Python 3.13 is not yet fully supported by FastAPI/Pydantic tooling or PyCharm’s indexer. Explicitly locking Python to 3.12 and binding the backend virtual environment to PyCharm ensures stable imports and predictable tooling behavior.

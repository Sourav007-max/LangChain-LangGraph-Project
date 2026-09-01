# Operational Architecture

```text
React UI
  -> FastAPI application/API layer
  -> LangGraph business workflow and shared utilities
  -> SQLAlchemy data access
  -> SQLite (development) or MySQL (production)
```

## Operational modules

- `frontend/src/`: pages, reusable UI components, client services, state, and TypeScript types.
- `backend/main.py`: FastAPI application, request validation, authentication dependencies, and API handlers.
- `agents/`: hiring workflow state, graph routing, agent nodes, and prompt templates.
- `database/`: SQLAlchemy session management, operational ORM models, initialization, and MySQL DDL.
- `config/`: environment-backed settings, LLM provider factory, and monitoring.
- `utils/`: shared password and resume document helpers.

The application dependency direction is one-way: UI -> API -> business logic -> data access. `docs/learning/` is static educational material and has no runtime imports.

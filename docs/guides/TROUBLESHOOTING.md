# Troubleshooting

## Database connection errors

Development defaults to SQLite. If `.env` sets `DATABASE_URL` to MySQL, verify the database exists and the configured user can connect.

## Missing API keys

Set `DEFAULT_LLM_PROVIDER` and its matching key in `.env`:

- `groq` -> `GROQ_API_KEY`
- `gemini` -> `GOOGLE_API_KEY`
- `openai` -> `OPENAI_API_KEY`
- `anthropic` -> `ANTHROPIC_API_KEY`

## Port already in use

Stop the existing API process or start Uvicorn on another port. Update the frontend API base URL if needed.

## Frontend dependencies

Run `npm install` from `frontend/`, then run `npm run build` to check the TypeScript and Vite build.

## Tests

Run `python -m pytest tests/test_e2e_workflow.py -q` for the local mocked workflow tests. Live integration tests require a running API, database, and configured LLM provider.

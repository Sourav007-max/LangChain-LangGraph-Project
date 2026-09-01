# API Reference

The backend runs at `http://localhost:8000` and exposes interactive OpenAPI documentation at `/docs`.

## Public

- `GET /health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

## Jobs and resumes

- `GET /api/v1/jobs`
- `POST /api/v1/jobs`
- `GET /api/v1/jobs/{job_id}`
- `POST /api/v1/resumes/upload`

## Workflows

- `POST /api/v1/workflows/start` runs the LangGraph workflow until human review.
- `GET /api/v1/workflows/{thread_id}/state` returns the current workflow snapshot.
- `POST /api/v1/workflows/{thread_id}/approve` resumes the workflow with the recruiter's decision.

## Operational visibility

- `GET /api/v1/analytics/dashboard`
- `GET /api/v1/monitoring/stats`
- `GET /api/v1/monitoring/logs`

Protected routes require `Authorization: Bearer <token>`. Recruiter and admin roles can create jobs, upload resumes, and start workflows; hiring managers can approve shortlisted candidates.

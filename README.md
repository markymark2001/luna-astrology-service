# Luna Astrology Service

FastAPI astrology compute service powered by
[Kerykeion](https://github.com/g-battaglia/kerykeion). This service is kept as a
separate runtime and public sync target to preserve the AGPL boundary.

## Runtime Boundary

The main backend must treat this service as an HTTP dependency. Do not add Python
cross-imports between `backend/` and `astrology-service/`.

Each endpoint under `app/api/v1/` must include a caller comment:

```python
# Called by: backend/app/infrastructure/repositories/http_astrology_repository.py
```

The repository contract checker verifies endpoint ownership and caller count.
See [../docs/architecture.md](../docs/architecture.md) and
[../docs/contracts.md](../docs/contracts.md).

## Current API Surface

All v1 routes are mounted under `/api/v1` and require the internal service token
dependency configured in `app/api/v1/__init__.py`.

- `POST /api/v1/astrology/profile`
- `POST /api/v1/astrology/profile/lookup`
- `POST /api/v1/astrology/profile/monthly`
- `POST /api/v1/astrology/profile/placements`
- `POST /api/v1/astrology/synastry`
- `POST /api/v1/astrology/transits/period`
- `GET /health`

Request models live in `app/models/requests.py`; response models live in
`app/models/responses.py`.

## Local Development

From the repository root, VSCode can launch the full stack through
`Full Stack Development`. Direct service run:

```bash
PYTHONPATH=astrology-service \
.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Focused tests:

```bash
PYTHONPATH=astrology-service .venv/bin/pytest astrology-service/tests/path/to/test.py -v
```

## License

This service is AGPL-3.0 because it uses Kerykeion. It is automatically synced
to the public astrology-service repository for source availability.

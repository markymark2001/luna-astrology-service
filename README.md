# Luna Astrology Service

A FastAPI-based astrology calculation service powered by [Kerykeion](https://github.com/g-battaglia/kerykeion). This service provides REST API endpoints for calculating natal birth charts with planetary positions, house cusps, and aspects.

## Features

- **Natal Chart Calculation**: Calculate complete birth charts with planetary positions, houses, and aspects
- **RESTful API**: Clean, versioned API design (v1)
- **Type Safety**: Full Pydantic validation for requests and responses
- **Extensible Architecture**: Designed to support future features (synastry, transits, progressions)
- **Production Ready**: Railway deployment with health checks

## Tech Stack

- **FastAPI**: Modern Python web framework
- **Kerykeion**: Astrology calculations library
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server

## API Documentation

### Endpoints

#### Health Check
```
GET /health
```

Returns service health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "Luna Astrology Service",
  "version": "1.0.0",
  "environment": "dev"
}
```

#### Calculate Natal Chart
```
POST /api/v1/natal/calculate
```

Calculate a natal birth chart from birth data.

**Request Body:**
```json
{
  "year": 1990,
  "month": 3,
  "day": 15,
  "hour": 14,
  "minute": 30,
  "latitude": 40.7128,
  "longitude": -74.0060,
  "timezone": "America/New_York"
}
```

**Response:**
```json
{
  "planets": [
    {
      "name": "Sun",
      "sign": "Pisces",
      "degree": 24.5,
      "absolute_degree": 354.5,
      "house": 10,
      "retrograde": false,
      "element": "Water",
      "quality": "Mutable"
    }
  ],
  "houses": [
    {
      "number": 1,
      "sign": "Gemini",
      "degree": 15.2,
      "absolute_degree": 75.2
    }
  ],
  "aspects": [
    {
      "planet1": "Sun",
      "planet2": "Moon",
      "aspect_type": "trine",
      "orb": 2.1,
      "applying": true
    }
  ],
  "ascendant": 75.2,
  "midheaven": 345.8,
  "chart_type": "Natal"
}
```

## Local Development

### Prerequisites

- Python 3.10+
- pip

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd luna-astrology-service
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

5. **Access the API:**
   - API Root: http://localhost:8001
   - Interactive Docs: http://localhost:8001/docs
   - Alternative Docs: http://localhost:8001/redoc
   - Health Check: http://localhost:8001/health

### Testing with curl

```bash
curl -X POST "http://localhost:8001/api/v1/natal/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "year": 1990,
    "month": 3,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York"
  }'
```

## Deployment

### Railway

This service is configured for Railway deployment.

1. **Create Railway service:**
   ```bash
   railway init
   ```

2. **Deploy:**
   ```bash
   railway up
   ```

3. **Configure environment variables (optional):**
   ```bash
   railway variables set ENV=prod
   railway variables set DEBUG=false
   ```

Railway will automatically:
- Detect Python via `.python-version`
- Install dependencies from `requirements.txt`
- Run the web server from `Procfile`
- Monitor health via `/health` endpoint

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENV` | `dev` | Environment name |
| `DEBUG` | `false` | Enable debug mode |
| `PORT` | `8001` | Server port (Railway sets this automatically) |

## Project Structure

```
luna-astrology-service/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   └── v1/
│   │       ├── natal.py     # Natal chart endpoints
│   │       ├── synastry.py  # (Future) Compatibility
│   │       ├── transits.py  # (Future) Transits
│   │       └── progressions.py  # (Future) Progressions
│   ├── services/
│   │   └── kerykeion_service.py  # Kerykeion wrapper
│   ├── models/
│   │   ├── requests.py      # Request models
│   │   └── responses.py     # Response models
│   ├── config/
│   │   └── settings.py      # Configuration
│   └── core/
│       └── exceptions.py    # Custom exceptions
├── requirements.txt
├── Procfile                 # Railway deployment
├── railway.toml            # Railway configuration
└── README.md
```

## Future Features

The architecture is designed to support additional astrology features:

- **Synastry**: Relationship compatibility analysis between two charts
- **Transits**: Current planetary transits and their effects
- **Progressions**: Secondary progressions for predictive astrology
- **Solar Returns**: Annual solar return charts

These will be added as new endpoints under `/api/v1/`.

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the LICENSE file for details.

This license is required due to the use of [Kerykeion](https://github.com/g-battaglia/kerykeion), which is also licensed under AGPL-3.0.

## Credits

- **Kerykeion**: Astrology library by Giacomo Battaglia
- **FastAPI**: Modern Python web framework
- **Luna**: Parent project by Mark Vasilyev

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue on GitHub.

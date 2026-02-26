# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-02-26

### Added
- REST API with FastAPI for credit score simulation (0-1000)
- POST `/score/calcular` endpoint with Pydantic validation
- GET `/score/historico` endpoint for querying previous scores
- GET `/` and `/health` endpoints for API info and status
- Score calculation based on 5 factors: income, debt ratio, payment history, credit history length, and recent inquiries
- Risk classification in 4 levels: low, medium, high, and very high
- Detailed analysis with positive/negative factors and recommendations
- Automatic input validation with Pydantic (ClienteInput)
- StatusPagamento enum with 4 states: em_dia, atraso_leve, atraso_grave, inadimplente
- CORS enabled for frontend and dashboard consumption
- Web interface (HTML/CSS/JS) for visual score simulation
- INICIAR.bat script for automated execution on Windows
- Unit tests with Pytest
- Integration with the Credit Score Ecosystem (Analysis, ETL, Dashboard)

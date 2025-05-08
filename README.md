# What to Cook Today

A recipe recommendation application that helps you decide what to cook today!

## Quality report 

Quality report of this project can be found at this link: [Quality Report](REPORT.md)

## Features

- Get random recipe suggestions
- Search recipes by name or ingredient
- Save favorite recipes
- Add custom recipes
- Browse recipes offline

## Setup

1. Install Python 3.12 or higher
2. Install dependencies using poetry:

   ```bash
   poetry install --no-root
   ```

## Running the Application

1. Start the FastAPI server:

   ```bash
   poetry run python -m src
   ```

2. The API will be available at `http://localhost:8000`

3. Access the API documentation at `http://localhost:8000/docs`

## API Endpoints

- `GET /recipes/random` - Get a random recipe
- `GET /recipes/search` - Search recipes by name or ingredient
- `GET /recipes/favorites` - Get all favorite recipes
- `GET /recipes/custom` - Get all custom recipes
- `POST /recipes/{recipe_id}/favorite` - Toggle favorite status for a recipe
- `POST /recipes/custom` - Add a custom recipe

## User Interface

The application implements a Streamlit-based web interface with the following functionality:

- Recipe display with image, ingredients and instructions
- Recipe search with text input
- Recipe management operations
- Form-based recipe creation

### Running the UI

1. Ensure API server is running (port 8000)
2. Execute UI server:

   ```bash
   poetry --directory src/ui run streamlit run app.py
   ```

3. Access UI at `http://localhost:8501`

## Quality Requirements

The project must maintain the following quality metrics:

- Maintainability:
  - Cyclomatic Complexity ≤ 20 per function/method
  - Code Duplication ≤ 5%
  - Propagation cost ≤ 15%

- Reliability:
  - Unit test coverage ≥ 65%

- Performance:
  - Response time during execution of listed functional requirements ≤ 0.2 ms
  - Response time during API calls ≤ 2 s

- Security:
  - 0 critical vulnerabilities
  - Fuzzing testing ≥ 80% branch coverage

## Development

### Running Tests

```bash
poetry run python -m pytest
```

### Code Quality

The project uses ruff for linting and formatting. Run:

```bash
ruff check .
ruff format .
```

### Maintainability Checks

The project maintains strict maintainability requirements:

- Cyclomatic Complexity ≤ 20 per function/method
- Code Duplication ≤ 5%
- Propagation cost ≤ 15%

To check these metrics:

```bash
# Check cyclomatic complexity
poetry run radon cc src -a

# Check code duplication
poetry run pylint --disable=all --enable=duplicate-code src

# Check propagation cost
poetry run pylint --disable=all --enable=design src
```

### Performance Testing

The application includes performance testing using Locust. To run performance tests:

```bash
# Basic load test (10 users, 10 spawn rate, 1 minute)
poetry run locust -f tests/load_test/locustfile.py -H http://localhost:8000 --headless -u 10 -r 10 --run-time 1m

# Interactive load test (web interface)
poetry run locust -f tests/load_test/locustfile.py -H http://localhost:8000
```

Performance metrics:

- Average response time: 143ms
- 90th percentile response time: 300ms
- Throughput: 4.79 requests/second
- Error rate: 0%

### Security Testing

Security testing is performed using Bandit. To run security checks:

```bash
poetry run bandit -r src --exclude src/ui/.venv
```

### Fuzzing Tests

The project includes fuzzing tests using Hypothesis. These tests are automatically run with pytest, but you can run them specifically:

```bash
poetry run python -m pytest tests/fuzzing -v --cov=src --cov-config=.fuzz-coveragerc
```

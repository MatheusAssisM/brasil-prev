# Brasil Prev - Monopoly Game Simulator

A Python-based simulation of a simplified Monopoly-style board game with clean architecture, strategy pattern implementation, and FastAPI HTTP endpoints.

## Features

- **Clean Architecture**: Hexagonal architecture with clear separation of layers
- **Domain-Driven Design**: Core business logic isolated from infrastructure concerns
- **Strategy Pattern**: 4 distinct player behaviors without conditional logic
  - **Impulsive**: Always buys properties when possible
  - **Demanding**: Only buys properties with rent above 50
  - **Cautious**: Only buys if balance remains above 80 after purchase
  - **Random**: 50% chance to buy any property
- **Factory Pattern**: Centralized player creation with `PlayerFactory`
- **Repository Pattern**: In-memory property repository for entity storage
- **Dependency Injection**: Container-based DI for loose coupling
- **Parallel Processing**: Multi-core batch simulations for high performance
- **Comprehensive Type Hints**: Full typing support using Python's `typing` module
- **Game Rules**:
  - 20 properties with random costs (50-200) and rents (10-100)
  - 4 players start with 300 balance
  - Players earn 100 salary per complete board round
  - Elimination when balance < 0
  - Victory: Last player standing OR highest balance after 1000 rounds
- **FastAPI REST API**: Run single or batch simulations via HTTP with performance metrics

## Project Structure

```
brasil-prev/
├── app/
│   ├── core/                      # Core abstractions and configurations
│   │   ├── interfaces.py          # Abstract interfaces (Strategy, Repository, etc.)
│   │   ├── config.py              # GameConfig, Settings
│   │   └── exceptions.py          # Custom exceptions
│   │
│   ├── domain/                    # Domain layer (business rules)
│   │   ├── models.py              # Player, Property, Board, GameState
│   │   ├── strategies.py          # Strategy implementations
│   │   ├── factories.py           # Player factory
│   │   └── engine.py              # Game engine (turn execution, rules)
│   │
│   ├── application/               # Application layer (use cases)
│   │   ├── simulator.py           # Game simulation orchestration
│   │   └── worker.py              # Worker for parallel processing
│   │
│   ├── infrastructure/            # Infrastructure layer
│   │   ├── api/                   # HTTP interface
│   │   │   └── routes.py          # FastAPI endpoints and models
│   │   ├── persistence/           # Data persistence
│   │   │   └── repositories.py    # Property repository implementation
│   │   ├── generators/            # Random generators
│   │   │   └── random.py          # Dice roller, board generator
│   │   ├── logging/               # Structured logging
│   │   │   └── logger.py          # JSON logger configuration
│   │   └── di/                    # Dependency injection
│   │       └── container.py       # DI container
│   │
│   └── main.py                    # FastAPI app entrypoint
│
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   └── integration/               # Integration tests
│
├── COMMENTS.md                    # Step-by-step execution guide
└── pyproject.toml                 # Project configuration
```

## Installation & Usage

### Quick Start with Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd brasil-prev

# Start the application
make docker-up

# Sem docker
cp .env-sample .env
make install
make run
```

The server will start at `http://localhost:8000`

**Stop the application:**
```bash
make docker-down
```

### Local Development Setup (Optional)

For development, you'll need:
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

```bash
# Install dependencies and setup hooks
make setup-dev
```

**Environment Configuration:**

Copy `.env-sample` to `.env` and adjust settings as needed:
```bash
cp .env-sample .env
```

All settings have defaults and can be overridden via environment variables prefixed with `MONOPOLY_`. See `.env-sample` for available options.

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Run Single Game Simulation
```bash
curl -X POST http://localhost:8000/game/simulate
```

**Response:**
```json
{
  "winner": "impulsive",
  "players": ["impulsive", "demanding", "cautious", "random"]
}
```

#### Run Batch Simulations
```bash
curl -X POST http://localhost:8000/simulations/benchmark \
  -H "Content-Type: application/json" \
  -d '{"num_simulations": 300}'
```

**Response:**
```json
{
  "total_simulations": 300,
  "timeouts": 15,
  "timeout_rate": 0.05,
  "avg_rounds": 342.5,
  "strategy_statistics": [
    {
      "strategy": "impulsive",
      "wins": 120,
      "win_rate": 0.40,
      "timeouts": 15,
      "avg_rounds_when_won": 285.3
    },
    ...
  ],
  "most_winning_strategy": "impulsive",
  "execution_time_seconds": 2.45,
  "simulations_per_second": 122.45,
  "parallelization_enabled": true,
  "num_workers": 8
}
```

### Interactive API Documentation

Visit `http://localhost:8000/` for Swagger UI documentation.

## Development

### Quick Setup for New Developers

**Requirements:** Python 3.13+ and [uv](https://github.com/astral-sh/uv) installed.

```bash
# Automated setup (installs dependencies + configures pre-push hooks)
make setup-dev
```

This will:
- Install all dependencies (including dev tools)
- Configure pre-push hooks for code quality checks
- Format code and run initial quality checks

### Run Tests

This project separates unit tests (fast, isolated) from integration tests (API, E2E flows):

```bash
# Run unit tests
make test-unit

# Run integration tests (API, E2E)
make test-integration

# Run unit tests with coverage report
make coverage
```

### Code Quality Tools

This project uses multiple tools to ensure code quality:

#### Formatter
- **Black**: Opinionated code formatter
```bash
make format
```

#### Linters
- **Flake8**: Style guide enforcement
- **Pylint**: Code analysis for bugs and quality
```bash
make lint
```

#### Type Checker
- **MyPy**: Static type checking
```bash
make typecheck
```

#### Run All Quality Checks
```bash
# Format + Lint + Type Check (no tests)
make quality
```

### Pre-push Hook

A pre-push git hook is automatically configured via `make setup-dev`. It runs:
1. Black (format check)
2. Flake8
3. Pylint
4. MyPy
5. Unit Tests (pytest -m unit)

If any check fails, the push is blocked. This ensures all code pushed to the repository meets quality standards.

**Note:** You can still run the application via Docker without running `make setup-dev`. The setup is only needed for local development and contributing.

## Architecture Decisions

### Strategy Pattern
Player behaviors are implemented as strategies without conditional logic inside player classes. This:
- Keeps business logic separate from player state
- Makes strategies easily testable and extensible
- Follows Open/Closed Principle

### Factory Pattern
`PlayerFactory` centralizes player creation logic:
- Encapsulates strategy instantiation
- Provides convenient methods for creating players with different strategies
- Makes it easy to change default configurations
- Enables consistent player creation across the application

Example:
```python
from app.game.factories import PlayerFactory

# Create individual players
impulsive = PlayerFactory.create_impulsive_player("Alice")
cautious = PlayerFactory.create_cautious_player("Bob", balance=500)

# Create default set of players
players = PlayerFactory.create_default_players()
```

### Domain-Driven Design
Clear separation between:
- **Domain Layer**: Pure business logic and rules
- **Engine Layer**: Game orchestration
- **API Layer**: HTTP interface and serialization
- **Strategy Layer**: Behavior patterns

### Game Rules Enforcement
All game rules are centralized in `GameEngine`:
- Dice rolling and movement
- Property purchase logic
- Rent payment flow
- Elimination and victory conditions

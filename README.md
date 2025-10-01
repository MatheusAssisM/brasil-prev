# Brasil Prev - Monopoly Game Simulator

A Python-based simulation of a simplified Monopoly-style board game with clean architecture, strategy pattern implementation, and FastAPI HTTP endpoints.

## Features

- **Clean Domain-Driven Design**: Separation of concerns with domain models, strategies, and game engine
- **Strategy Pattern**: 4 distinct player behaviors without conditional logic
  - **Impulsive**: Always buys properties when possible
  - **Demanding**: Only buys properties with rent above 50
  - **Cautious**: Only buys if balance remains above 80 after purchase
  - **Random**: 50% chance to buy any property
- **Game Rules**:
  - 20 properties with random costs (50-200) and rents (10-100)
  - 4 players start with 300 balance
  - Players earn 100 salary per complete board round
  - Elimination when balance < 0
  - Victory: Last player standing OR highest balance after 1000 rounds
- **FastAPI REST API**: Run single or batch simulations via HTTP
- **Comprehensive Tests**: 44+ tests covering all components

## Project Structure

```
monopoly-simulator-api/
├── app/
│   ├── core/               # Contracts, abstractions, configs
│   │   ├── interfaces.py   # EstrategiaCompra interface
│   │   └── config.py       # GameConfig, Settings
│   │
│   ├── game/               # Domain logic (business rules)
│   │   ├── models.py       # Player, Property, Board, GameState
│   │   ├── strategies.py   # Strategy implementations
│   │   └── engine.py       # Game engine (turn execution, rules)
│   │
│   ├── services/           # Application services (use cases)
│   │   └── simulator.py    # Game simulation orchestration
│   │
│   ├── api/                # HTTP interface (infrastructure)
│   │   └── routes.py       # FastAPI endpoints and models
│   │
│   ├── utils/              # Helper utilities
│   │   └── randomizer.py   # Dice rolls, board generation
│   │
│   └── main.py             # FastAPI app entrypoint
│
├── tests/                  # Test suite (44 tests)
│   ├── test_strategies.py
│   ├── test_domain.py
│   ├── test_game_engine.py
│   └── test_api.py
│
├── COMMENTS.md             # Step-by-step execution guide
├── ARCHITECTURE.md         # Architecture documentation
└── pyproject.toml          # Project configuration
```

## Installation

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd brasil-prev

# Install dependencies
uv sync

# Install in editable mode
uv pip install -e .
```

## Usage

### Start the API Server

```bash
uv run start
```

The server will start at `http://localhost:8000`

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/
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
curl -X POST http://localhost:8000/game/stats \
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
  "most_winning_strategy": "impulsive"
}
```

### Interactive API Documentation

Visit `http://localhost:8000/docs` for Swagger UI documentation.

## Development

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=brasil_prev --cov-report=html

# Run specific test file
uv run pytest tests/test_strategies.py
```

### Run Linting

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

## Architecture Decisions

### Strategy Pattern
Player behaviors are implemented as strategies without conditional logic inside player classes. This:
- Keeps business logic separate from player state
- Makes strategies easily testable and extensible
- Follows Open/Closed Principle

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

This ensures consistency and makes the rules easy to verify and modify.

## License

MIT

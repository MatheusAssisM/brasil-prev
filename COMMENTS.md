# Step-by-Step Execution Guide

This document provides a comprehensive guide to understanding, running, and testing the Monopoly Simulator API.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Running the Application](#running-the-application)
5. [API Endpoints](#api-endpoints)
6. [Running Tests](#running-tests)
7. [Code Walkthrough](#code-walkthrough)
8. [Design Decisions](#design-decisions)

## Project Overview

This is a simplified Monopoly-style board game simulator built with clean architecture principles. The system simulates matches between 4 players, each using a different strategy for property purchases.

### Game Rules

- **Board**: 20 properties with random purchase costs (50-200) and rents (10-100)
- **Players**: 4 players starting with 300 balance
- **Turns**:
  - Roll 1d6 dice
  - Move clockwise around board
  - Land on property → buy (if unowned) or pay rent (if owned by other player)
  - Complete a round → earn 100 salary
- **Elimination**: Balance < 0 → player eliminated, properties released
- **Victory**: Last player standing OR highest balance after 1000 rounds

### Player Strategies

1. **Impulsive**: Always buys when possible
2. **Demanding**: Only buys if rent > 50
3. **Cautious**: Only buys if balance after purchase ≥ 80
4. **Random**: 50% chance to buy

## Architecture

### Layer Organization

```
app/
├── core/           # Contracts, interfaces, configuration
│   ├── interfaces.py   # PurchaseStrategy (Strategy interface)
│   └── config.py       # GameConfig, Settings
│
├── game/           # Domain logic (business rules)
│   ├── models.py       # Property, Player, Board, GameState
│   ├── strategies.py   # ImpulsiveStrategy, DemandingStrategy, etc.
│   └── engine.py       # GameEngine (turn execution, rule enforcement)
│
├── services/       # Application services (use cases)
│   └── simulator.py    # GameSimulator (orchestrates simulations)
│
├── api/            # HTTP interface (infrastructure)
│   └── routes.py       # FastAPI endpoints, Pydantic models
│
├── utils/          # Helper utilities
│   └── randomizer.py   # Dice rolling, board generation
│
└── main.py         # FastAPI app entrypoint
```

### Key Design Patterns

- **Strategy Pattern**: Player behaviors are decoupled via `PurchaseStrategy` interface
- **Dependency Injection**: Dice roller can be injected into GameEngine (facilitates testing)
- **Clean Architecture**: Domain logic is independent of infrastructure concerns

## Installation

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup Steps

```bash
# 1. Clone repository
git clone <repository-url>
cd brasil-prev

# 2. Install dependencies
uv sync

# 3. Install package in editable mode
uv pip install -e .
```

## Running the Application

### Start the API Server

```bash
# Using the configured script
uv run start

# OR using uvicorn directly
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### 1. Health Check

```bash
GET /
GET /health
```

**Example:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "monopoly-simulator-api",
  "version": "1.0.0"
}
```

### 2. Simulate Single Game

```bash
POST /game/simulate
```

**Example:**
```bash
curl -X POST http://localhost:8000/game/simulate
```

**Response:**
```json
{
  "winner": "Impulsive Player",
  "rounds": 127,
  "timeout": false,
  "players": [
    {
      "name": "Impulsive Player",
      "strategy": "Impulsive",
      "balance": 1453,
      "properties_owned": 15,
      "is_active": true
    },
    ...
  ]
}
```

### 3. Batch Simulation (Statistics)

```bash
POST /game/stats
Content-Type: application/json

{
  "num_simulations": 300
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/game/stats \
  -H "Content-Type: application/json" \
  -d '{"num_simulations": 300}'
```

**Response:**
```json
{
  "total_simulations": 300,
  "timeouts": 12,
  "timeout_rate": 0.04,
  "avg_rounds": 345.2,
  "strategy_statistics": [
    {
      "strategy": "Impulsive",
      "wins": 125,
      "win_rate": 0.42,
      "timeouts": 12,
      "avg_rounds_when_won": 287.5
    },
    ...
  ],
  "most_winning_strategy": "Impulsive"
}
```

## Running Tests

### Run All Tests

```bash
uv run pytest
```

### Run with Verbose Output

```bash
uv run pytest -v
```

### Run Specific Test File

```bash
uv run pytest tests/test_strategies.py
uv run pytest tests/test_game_engine.py
uv run pytest tests/test_api.py
```

### Run with Coverage

```bash
uv run pytest --cov=app --cov-report=html
```

### Test Organization

- **test_strategies.py**: Unit tests for each strategy implementation
- **test_domain.py**: Unit tests for domain models (Property, Player, Board, GameState)
- **test_game_engine.py**: Unit tests for game engine logic and rule enforcement
- **test_api.py**: Integration tests for API endpoints

## Code Walkthrough

### 1. Starting Point: Main Entry

**File**: `app/main.py`

```python
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(...)
app.include_router(router)  # Register API routes
```

The FastAPI application is created and routes are registered from `app/api/routes.py`.

### 2. API Layer

**File**: `app/api/routes.py`

```python
@router.post("/game/simulate", response_model=GameResult)
async def simulate_game():
    result = GameSimulator.run_single_simulation()
    return GameResult(...)
```

Routes delegate to `GameSimulator` service and return Pydantic-validated responses.

### 3. Service Layer

**File**: `app/services/simulator.py`

```python
class GameSimulator:
    @staticmethod
    def run_single_simulation() -> dict:
        players = GameSimulator.create_default_players()
        board = generate_board()
        engine = GameEngine(players, board)
        engine.set_dice_roller(roll_dice)
        engine.play_game()
        return engine.get_game_result()
```

The simulator orchestrates:
1. Creating players with strategies
2. Generating a random board
3. Running the game engine
4. Formatting results

### 4. Game Engine

**File**: `app/game/engine.py`

```python
class GameEngine:
    def play_game(self) -> GameState:
        while not self.state.game_over:
            self.play_round()
            self.state.check_victory_condition()
        return self.state

    def play_turn(self, player: Player) -> None:
        steps = self.roll_dice()
        player.move(steps, self.state.board.size())
        property = self.state.board.get_property(player.position)
        self._handle_property_landing(player, property)
```

The engine enforces all game rules:
- Turn execution (dice roll, movement, property interaction)
- Round completion (all players take turns)
- Victory condition checking

### 5. Domain Models

**File**: `app/game/models.py`

```python
class Player:
    def buy_property(self, property: Property) -> bool:
        if not self.can_buy(property.cost):
            return False
        if self.strategy.should_buy(self, property):  # Strategy decides!
            self.balance -= property.cost
            ...
            return True
        return False
```

**Key insight**: Player delegates decision to its `strategy`, following the Strategy Pattern.

### 6. Strategy Implementation

**File**: `app/game/strategies.py`

```python
class ImpulsiveStrategy(PurchaseStrategy):
    def should_buy(self, player: Player, property: Property) -> bool:
        return True  # Always buy!

class DemandingStrategy(PurchaseStrategy):
    def should_buy(self, player: Player, property: Property) -> bool:
        return property.rent > self.rent_threshold  # Conditional
```

Each strategy implements `PurchaseStrategy` interface with pure decision logic—no access to Player internals.

## Design Decisions

### 1. Why Strategy Pattern?

**Problem**: Different players need different behaviors without coupling behavior to Player class.

**Solution**: Extract behavior to separate strategy classes implementing a common interface.

**Benefits**:
- Easy to add new strategies without modifying Player
- Strategies are independently testable
- Follows Open/Closed Principle

### 2. Why Separate Randomizer Utility?

**Reasoning**:
- Centralizes all randomization logic
- Makes testing easier (can mock dice rolls)
- GameEngine doesn't depend directly on `random` module

### 3. Why Inject Dice Roller?

**Reasoning**:
- Allows deterministic testing (inject custom dice roller)
- Follows Dependency Inversion Principle
- Engine doesn't know _how_ dice are rolled, just _that_ they are

### 4. Why Separate GameState from GameEngine?

**Reasoning**:
- GameState is pure data (players, board, round count)
- GameEngine contains behavior (executing turns, enforcing rules)
- Separation of concerns: state management vs. game logic

### 5. Why Domain Models Don't Know About API?

**Reasoning**:
- Domain logic should be independent of delivery mechanism
- Models can be reused in CLI, GUI, or other interfaces
- Follows Clean Architecture: domain at the center, infrastructure at edges

## Conclusion

This implementation demonstrates:
- **Clean Architecture**: Clear separation between domain, application, and infrastructure layers
- **Strategy Pattern**: Behavior encapsulation and polymorphism
- **Testability**: Comprehensive test coverage with 44 tests
- **Extensibility**: Easy to add new strategies, rules, or interfaces

The codebase prioritizes:
1. Readability
2. Maintainability
3. Testability
4. Adherence to SOLID principles

---

**Generated**: 2025-01-01
**Version**: 1.0.0

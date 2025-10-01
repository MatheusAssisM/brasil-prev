# Architecture Documentation

## Overview

This project implements a Monopoly-style board game simulation using clean architecture principles, the strategy pattern, and domain-driven design.

## Core Principles

### 1. Separation of Concerns

The codebase is organized into distinct layers:

```
Domain Layer (Pure Business Logic)
    ↓
Strategy Layer (Behavior Patterns)
    ↓
Engine Layer (Game Orchestration)
    ↓
API Layer (HTTP Interface)
```

### 2. Strategy Pattern Implementation

**Problem**: Different players need different decision-making behaviors without adding conditional logic inside the Player class.

**Solution**: Each player type implements the `PlayerStrategy` interface:

```python
class PlayerStrategy(ABC):
    @abstractmethod
    def should_buy(self, player: Player, property: Property) -> bool:
        pass
```

**Benefits**:
- Players are decoupled from decision logic
- Easy to add new strategies without modifying existing code
- Each strategy is independently testable
- Follows Open/Closed Principle

### 3. Domain Models

#### Property
Represents a board space that can be owned and generates rent.

**Responsibilities**:
- Store cost and rent values
- Track ownership
- Provide ownership transfer methods

#### Player
Represents a game participant with balance, position, and properties.

**Responsibilities**:
- Manage balance and properties
- Move around the board
- Delegate purchase decisions to strategy
- Handle elimination

#### Board
Represents the game board with 20 properties.

**Responsibilities**:
- Generate random properties
- Provide property access by position

#### GameState
Tracks the overall game status.

**Responsibilities**:
- Track active players
- Count rounds
- Determine victory conditions

### 4. Game Engine

The `GameEngine` class orchestrates the game flow:

```
Game Loop:
1. Get active players
2. For each player:
   a. Roll dice
   b. Move player
   c. Handle property landing:
      - If unowned: attempt purchase (via strategy)
      - If owned by other: pay rent
   d. Check elimination
3. Increment round
4. Check victory condition
5. Repeat until game over
```

**Key Design Decision**: All game rules are centralized in the engine, not distributed across domain models. This makes rules easy to understand, test, and modify.

### 5. API Layer

FastAPI provides a clean HTTP interface:

- **Models (Pydantic)**: Request/response validation and serialization
- **Service Layer**: Business logic coordination
- **App**: Route definitions and error handling

**Endpoints**:
- `POST /simulation/run` - Single game
- `POST /simulation/batch` - Multiple games with statistics

## Game Rules Implementation

### Movement
```python
# Player moves clockwise around board
new_position = (current_position + dice_roll) % board_size

# Salary when passing/landing on position 0
if completed_round:
    player.balance += 100
```

### Property Purchase
```python
if not property.is_owned() and player.can_buy(property.cost):
    # Delegate decision to strategy
    if player.strategy.should_buy(player, property):
        player.buy_property(property)
```

### Rent Payment
```python
if property.is_owned() and property.owner != player:
    player.pay_rent(property.rent)
    property.owner.receive_rent(property.rent)
```

### Elimination
```python
if player.balance < 0:
    player.eliminate()  # Releases all properties
```

### Victory Conditions
1. **Last Player Standing**: Only one active player remains
2. **Timeout**: 1000 rounds reached, winner = highest balance
3. **All Eliminated**: No winner (rare edge case)

## Testing Strategy

### Unit Tests
- **Strategies**: Test each decision algorithm in isolation
- **Domain Models**: Test state management and business rules
- **Game Engine**: Test game flow and rule enforcement

### Integration Tests
- **API Endpoints**: Test full request/response cycle
- **Game Simulation**: Test complete game execution

### Test Coverage
- 44 tests covering all major components
- Tests are isolated and deterministic (except Random strategy)

## Extension Points

The architecture makes it easy to add:

1. **New Strategies**: Implement `PlayerStrategy` interface
2. **New Rules**: Modify `GameEngine` methods
3. **New Endpoints**: Add routes to FastAPI app
4. **Analytics**: Extend `BatchSimulationResult` model
5. **Persistence**: Add repository layer between service and domain

## Performance Considerations

- Game simulation is CPU-bound (RNG and logic)
- Batch simulations run sequentially (could parallelize)
- No database required (stateless simulations)
- Memory usage is minimal (game state is small)

## Dependencies

**Production**:
- `fastapi`: Web framework
- `pydantic`: Data validation
- `uvicorn`: ASGI server

**Development**:
- `pytest`: Testing framework
- `httpx`: API testing client

All dependencies are managed via `uv` for fast, reproducible builds.

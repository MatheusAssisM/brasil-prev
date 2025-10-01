from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.simulator import GameSimulator

router = APIRouter()


# Request/Response Models
class GameResult(BaseModel):
    """Result of a single game simulation."""
    winner: Optional[str] = None
    players: List[str]


class BatchSimulationRequest(BaseModel):
    """Request to run multiple game simulations."""
    num_simulations: int = Field(
        default=300,
        ge=1,
        le=10000,
        description="Number of games to simulate"
    )


class StrategyStatistics(BaseModel):
    """Statistics for a specific strategy across multiple games."""
    strategy: str
    wins: int
    win_rate: float
    timeouts: int
    avg_rounds_when_won: float


class BatchSimulationResult(BaseModel):
    """Aggregated results from multiple game simulations."""
    total_simulations: int
    timeouts: int
    timeout_rate: float
    avg_rounds: float
    strategy_statistics: List[StrategyStatistics]
    most_winning_strategy: Optional[str] = None


# Routes
@router.post("/game/simulate", response_model=GameResult, tags=["Simulation"])
async def simulate_game():
    """
    Run a single game simulation with 4 players using different strategies.

    Returns the winner strategy name and list of all player strategies.
    """
    try:
        result = GameSimulator.run_single_simulation()

        # Extract winner strategy (lowercase)
        winner_strategy = None
        if result["winner"]:
            winner_player = next(p for p in result["players"] if p["name"] == result["winner"])
            winner_strategy = winner_player["strategy"]

        # Extract player strategies in order (lowercase)
        player_strategies = [p["strategy"] for p in result["players"]]

        return GameResult(
            winner=winner_strategy,
            players=player_strategies,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Game simulation failed: {str(e)}")


@router.post("/game/stats", response_model=BatchSimulationResult, tags=["Simulation"])
async def run_batch_simulation(request: BatchSimulationRequest):
    """
    Run multiple game simulations and return aggregated statistics.

    This endpoint is useful for analyzing which strategy performs best
    over many games and understanding average game characteristics.

    Args:
        request: BatchSimulationRequest with num_simulations parameter

    Returns:
        Aggregated statistics including win rates per strategy,
        average rounds, timeout rates, and most successful strategy.
    """
    try:
        result = GameSimulator.run_batch_simulation(request.num_simulations)

        return BatchSimulationResult(
            total_simulations=result["total_simulations"],
            timeouts=result["timeouts"],
            timeout_rate=result["timeout_rate"],
            avg_rounds=result["avg_rounds"],
            strategy_statistics=[
                StrategyStatistics(
                    strategy=s["strategy"],
                    wins=s["wins"],
                    win_rate=s["win_rate"],
                    timeouts=s["timeouts"],
                    avg_rounds_when_won=s["avg_rounds_when_won"],
                )
                for s in result["strategy_statistics"]
            ],
            most_winning_strategy=result["most_winning_strategy"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Batch simulation failed: {str(e)}"
        )

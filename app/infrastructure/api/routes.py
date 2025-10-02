from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.core.interfaces import SimulatorService
from app.infrastructure.di.container import get_simulator_service, get_logger

router = APIRouter()
logger = get_logger("app.infrastructure.api.routes")


# Request/Response Models
class GameResult(BaseModel):
    """Result of a single game simulation."""

    winner: Optional[str] = None
    players: List[str]


class BatchSimulationRequest(BaseModel):
    """Request to run multiple game simulations."""

    num_simulations: int = Field(
        default=300, ge=1, le=10000, description="Number of games to simulate"
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
async def simulate_game(
    simulator: SimulatorService = Depends(get_simulator_service),
) -> GameResult:
    """
    Run a single game simulation with 4 players using different strategies.

    Returns the winner strategy name and list of all player strategies.
    """
    try:
        result = simulator.run_single_simulation()

        winner_strategy = None
        if result["winner"]:
            winner_player = next(
                (p for p in result["players"] if p["name"] == result["winner"]), None
            )
            if winner_player:
                winner_strategy = winner_player["strategy"]

        player_strategies = [p["strategy"] for p in result["players"]]

        return GameResult(
            winner=winner_strategy,
            players=player_strategies,
        )
    except Exception as e:
        logger.error("Game simulation failed", extra={"error": str(e)}, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Game simulation failed: {str(e)}") from e


@router.post("/game/stats", response_model=BatchSimulationResult, tags=["Simulation"])
async def run_batch_simulation(
    request: BatchSimulationRequest,
    simulator: SimulatorService = Depends(get_simulator_service),
) -> BatchSimulationResult:
    """
    Run multiple game simulations and return aggregated statistics.

    This endpoint is useful for analyzing which strategy performs best
    over many games and understanding average game characteristics.

    """
    try:
        result = simulator.run_batch_simulation(request.num_simulations)

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
        logger.error(
            "Batch simulation failed",
            extra={"num_simulations": request.num_simulations, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Batch simulation failed: {str(e)}") from e

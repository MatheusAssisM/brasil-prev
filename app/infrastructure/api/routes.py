from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field

from app.core.interfaces import SimulatorService
from app.core.config import settings
from app.infrastructure.di.container import get_simulator_service, get_logger
from app.infrastructure.api.rate_limiter import limiter

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
    """Aggregated results from multiple game simulations with performance metrics."""

    total_simulations: int
    timeouts: int
    timeout_rate: float
    avg_rounds: float
    strategy_statistics: List[StrategyStatistics]
    most_winning_strategy: Optional[str] = None
    execution_time_seconds: float = Field(description="Total execution time in seconds")
    simulations_per_second: float = Field(description="Throughput (simulations/second)")
    parallelization_enabled: bool = Field(
        description="Always True - parallel execution is always used"
    )
    num_workers: int = Field(description="Number of worker processes used for parallel execution")


# Routes
@router.post("/game/simulate", response_model=GameResult, tags=["Simulation"])
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def simulate_game(
    request: Request,  # pylint: disable=unused-argument
    simulator: SimulatorService = Depends(get_simulator_service),
) -> GameResult:
    """
    Run a single game simulation with 4 players using different strategies.

    Returns the winner strategy name and list of all player strategies.

    Note: request parameter is required by SlowAPI rate limiter decorator.
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

        sorted_players = sorted(result["players"], key=lambda p: p["balance"], reverse=True)
        player_strategies = [p["strategy"] for p in sorted_players]

        return GameResult(
            winner=winner_strategy,
            players=player_strategies,
        )
    except Exception as e:
        logger.error("Game simulation failed", extra={"error": str(e)}, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Game simulation failed: {str(e)}") from e


@router.post("/simulations/benchmark", response_model=BatchSimulationResult, tags=["Simulation"])
@limiter.limit(settings.RATE_LIMIT_BENCHMARK)
async def run_benchmark_simulation(
    request: Request,  # pylint: disable=unused-argument
    body: BatchSimulationRequest,
    simulator: SimulatorService = Depends(get_simulator_service),
) -> BatchSimulationResult:
    """
    Run multiple game simulations with parallel execution and performance benchmarking.

    This endpoint runs batch simulations using parallel processing across multiple CPU cores
    and provides detailed performance metrics including execution time and throughput.

    Note: request parameter is required by SlowAPI rate limiter decorator.
    """
    try:
        result = simulator.run_batch_simulation(body.num_simulations)

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
            execution_time_seconds=result["execution_time_seconds"],
            simulations_per_second=result["simulations_per_second"],
            parallelization_enabled=result["parallelization_enabled"],
            num_workers=result["num_workers"],
        )
    except Exception as e:
        logger.error(
            "Batch simulation failed",
            extra={"num_simulations": body.num_simulations, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Batch simulation failed: {str(e)}") from e

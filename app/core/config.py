from dataclasses import dataclass
from pydantic_settings import BaseSettings


@dataclass(frozen=True)
class StrategyConfig:
    """Configuration for player strategies."""

    # Demanding strategy configuration
    DEMANDING_RENT_THRESHOLD: int = 50

    # Cautious strategy configuration
    CAUTIOUS_RESERVE_THRESHOLD: int = 80

    # Random strategy probability
    RANDOM_BUY_PROBABILITY: float = 0.5


class GameConfig:
    """Game rules and constants."""

    # Board configuration
    NUM_PROPERTIES = 20
    MIN_PROPERTY_COST = 50
    MAX_PROPERTY_COST = 200
    MIN_PROPERTY_RENT = 10
    MAX_PROPERTY_RENT = 100

    # Player configuration
    INITIAL_BALANCE = 300
    ROUND_SALARY = 100

    # Game rules
    MAX_ROUNDS = 1000


# Global strategy configuration instance
strategy_config = StrategyConfig()


class Settings(BaseSettings):
    """Application settings (can be overridden via environment variables)."""

    APP_NAME: str = "Brasil Prev - Monopoly Simulator API"
    DEBUG: bool = False
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    DOC_URL: str = "/"

    LOG_LEVEL: str = "WARNING"

    # Parallelization settings
    ENABLE_PARALLEL: bool = True
    MAX_WORKERS: int = 0

    # Rate limiting settings
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_BENCHMARK: str = "10/minute"

    model_config = {
        "env_file": ".env",
        "env_prefix": "MONOPOLY_",
        "case_sensitive": False,
        "extra": "ignore",
    }


settings = Settings()

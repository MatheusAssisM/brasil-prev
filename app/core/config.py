from pydantic_settings import BaseSettings


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

    # Strategy thresholds
    DEMANDING_RENT_THRESHOLD = 50
    CAUTIOUS_RESERVE_THRESHOLD = 80


class Settings(BaseSettings):
    """Application settings (can be overridden via environment variables)."""

    model_config = {
        "env_prefix": "MONOPOLY_",
        "case_sensitive": False,
    }

    app_name: str = "Brasil Prev - Monopoly Simulator API"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    doc_url: str = "/"


settings = Settings()

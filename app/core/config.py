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

    APP_NAME: str = "Brasil Prev - Monopoly Simulator API"
    DEBUG: bool = False
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    DOC_URL: str = "/"

    LOG_LEVEL: str = "WARNING"


settings = Settings()

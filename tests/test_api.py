from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "monopoly-simulator-api"


class TestSimulationEndpoints:
    """Test simulation endpoints."""

    def test_run_single_simulation(self):
        """Test running a single game simulation."""
        response = client.post("/game/simulate")
        assert response.status_code == 200

        data = response.json()

        # Check response structure
        assert "winner" in data
        assert "players" in data

        # Winner should be lowercase strategy name or None
        if data["winner"]:
            valid_strategies = ["impulsive", "demanding", "cautious", "random"]
            assert data["winner"] in valid_strategies

        # Players should be list of 4 lowercase strategy names
        assert len(data["players"]) == 4
        assert isinstance(data["players"], list)
        for strategy in data["players"]:
            assert isinstance(strategy, str)
            assert strategy in ["impulsive", "demanding", "cautious", "random"]

    def test_batch_simulation_default(self):
        """Test batch simulation with default parameters."""
        response = client.post("/game/stats", json={"num_simulations": 10})
        assert response.status_code == 200

        data = response.json()

        # Check response structure
        assert "total_simulations" in data
        assert "timeouts" in data
        assert "timeout_rate" in data
        assert "avg_rounds" in data
        assert "strategy_statistics" in data
        assert "most_winning_strategy" in data

        # Verify simulations ran
        assert data["total_simulations"] == 10

        # Check strategy statistics
        assert len(data["strategy_statistics"]) == 4

        strategies = {stat["strategy"] for stat in data["strategy_statistics"]}
        assert strategies == {"impulsive", "demanding", "cautious", "random"}

        # Verify win counts add up (or less if timeouts)
        total_wins = sum(stat["wins"] for stat in data["strategy_statistics"])
        assert total_wins <= data["total_simulations"]

    def test_batch_simulation_custom_count(self):
        """Test batch simulation with custom simulation count."""
        response = client.post("/game/stats", json={"num_simulations": 50})
        assert response.status_code == 200

        data = response.json()
        assert data["total_simulations"] == 50

    def test_batch_simulation_validation(self):
        """Test batch simulation input validation."""
        # Test too few simulations
        response = client.post("/game/stats", json={"num_simulations": 0})
        assert response.status_code == 422  # Validation error

        # Test too many simulations
        response = client.post("/game/stats", json={"num_simulations": 20000})
        assert response.status_code == 422  # Validation error


class TestOpenAPIDocumentation:
    """Test OpenAPI documentation endpoints."""

    def test_openapi_schema_exists(self):
        """Test that OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_docs_endpoint(self):
        """Test that Swagger UI docs are accessible."""
        response = client.get("/")
        assert response.status_code == 200

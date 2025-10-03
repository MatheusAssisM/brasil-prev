import pytest


@pytest.mark.integration
class TestAPIErrorHandling:
    """Test error handling in API endpoints."""

    def test_batch_simulation_invalid_count(self, test_client):
        """Test batch simulation with invalid count."""
        response = test_client.post("/simulations/benchmark", json={"num_simulations": 0})
        assert response.status_code in [422, 500]

    def test_batch_simulation_negative_count(self, test_client):
        """Test batch simulation with negative count."""
        response = test_client.post("/simulations/benchmark", json={"num_simulations": -5})
        assert response.status_code in [422, 500]

    def test_batch_simulation_invalid_type(self, test_client):
        """Test batch simulation with wrong type."""
        response = test_client.post("/simulations/benchmark", json={"num_simulations": "not a number"})
        assert response.status_code == 422

    def test_batch_simulation_with_default_value(self, test_client):
        """Test batch simulation uses default when no value provided."""
        response = test_client.post("/simulations/benchmark", json={})

        assert response.status_code == 200
        data = response.json()
        assert data["total_simulations"] == 300


@pytest.mark.integration
@pytest.mark.slow
class TestEdgeCases:
    """Test edge cases in game simulation."""

    def test_batch_simulation_single_run(self, test_client):
        """Test batch simulation with just 1 simulation."""
        response = test_client.post("/simulations/benchmark", json={"num_simulations": 1})

        assert response.status_code == 200
        data = response.json()
        assert data["total_simulations"] == 1
        assert len(data["strategy_statistics"]) == 4

    def test_batch_simulation_large_count(self, test_client):
        """Test batch simulation with larger count."""
        response = test_client.post("/simulations/benchmark", json={"num_simulations": 50})

        assert response.status_code == 200
        data = response.json()
        assert data["total_simulations"] == 50
        assert data["most_winning_strategy"] is not None

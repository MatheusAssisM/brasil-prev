"""Game engine that orchestrates the game flow and enforces rules."""

from typing import List

from app.game.models import Player, Board, GameState, Property
from app.core.config import GameConfig


class GameEngine:
    """
    Main game engine that orchestrates the game flow and enforces rules.
    """

    def __init__(self, players: List[Player], board: Board):
        """
        Initialize the game engine.

        Args:
            players: List of players participating in the game
            board: Board instance with properties
        """
        self.state = GameState(
            players=players,
            board=board,
            max_rounds=GameConfig.MAX_ROUNDS
        )
        self.dice_roller = None  # Will be injected

    def set_dice_roller(self, dice_roller):
        """Inject dice roller dependency."""
        self.dice_roller = dice_roller

    def roll_dice(self) -> int:
        """Roll a standard 6-sided die."""
        if self.dice_roller:
            return self.dice_roller()
        # Fallback to default
        import random
        return random.randint(1, 6)

    def play_turn(self, player: Player) -> None:
        """
        Execute a single turn for a player.

        Args:
            player: The player whose turn it is
        """
        if not player.is_active:
            return

        # Roll dice and move
        steps = self.roll_dice()
        new_position = player.move(
            steps,
            self.state.board.size(),
            GameConfig.ROUND_SALARY
        )

        # Get property at new position
        property = self.state.board.get_property(new_position)

        # Handle property interaction
        self._handle_property_landing(player, property)

        # Check if player is eliminated
        if player.balance < 0:
            player.eliminate()

    def _handle_property_landing(self, player: Player, property: Property) -> None:
        """
        Handle what happens when a player lands on a property.

        Args:
            player: The player who landed on the property
            property: The property that was landed on
        """
        if not property.is_owned():
            # Property is available - try to buy it
            player.buy_property(property)
        elif property.owner != player:
            # Property is owned by another player - pay rent
            owner = property.owner
            player.pay_rent(property.rent)
            if owner.is_active:  # Only pay if owner is still active
                owner.receive_rent(property.rent)

    def play_round(self) -> None:
        """Play a complete round where each active player takes a turn."""
        active_players = self.state.get_active_players()

        for player in active_players:
            self.play_turn(player)

        self.state.increment_round()

    def play_game(self) -> GameState:
        """
        Play a complete game until victory condition is met.

        Returns:
            The final game state
        """
        while not self.state.game_over:
            self.play_round()
            self.state.check_victory_condition()

        return self.state

    def get_game_result(self) -> dict:
        """
        Get a summary of the game results.

        Returns:
            Dictionary containing game statistics
        """
        return {
            "winner": self.state.winner.name if self.state.winner else None,
            "rounds": self.state.round_count,
            "timeout": self.state.round_count >= self.state.max_rounds,
            "players": [
                {
                    "name": player.name,
                    "strategy": player.strategy.get_name(),
                    "balance": player.balance,
                    "properties_owned": len(player.properties),
                    "is_active": player.is_active,
                }
                for player in self.state.players
            ],
        }

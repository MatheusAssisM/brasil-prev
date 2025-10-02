from typing import Callable, Dict, Any, List, Optional
import uuid

from app.game.models import Player, Board, GameState, Property
from app.core.config import GameConfig
from app.utils.logger import get_logger, set_game_context, add_game_context_to_logger

logger = get_logger(__name__)
add_game_context_to_logger(logger)


class GameEngine:
    """
    Main game engine that orchestrates the game flow and enforces rules.
    """

    def __init__(self, players: List[Player], board: Board) -> None:
        """
        Initialize the game engine.

        Args:
            players: List of players participating in the game
            board: Board instance with properties
        """
        self.state: GameState = GameState(
            players=players,
            board=board,
            max_rounds=GameConfig.MAX_ROUNDS
        )
        self.dice_roller: Optional[Callable[[], int]] = None
        self.game_id = str(uuid.uuid4())

        logger.info(
            "Game initialized",
            extra={
                "game_id": self.game_id,
                "num_players": len(players),
                "player_strategies": [p.strategy.get_name() for p in players],
                "board_size": board.size()
            }
        )

    def set_dice_roller(self, dice_roller: Callable[[], int]) -> None:
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

        old_position = player.position
        old_balance = player.balance

        # Roll dice and move
        steps = self.roll_dice()
        new_position = player.move(
            steps,
            self.state.board.size(),
            GameConfig.ROUND_SALARY
        )

        logger.debug(
            "Player turn",
            extra={
                "player": player.name,
                "strategy": player.strategy.get_name(),
                "dice_roll": steps,
                "old_position": old_position,
                "new_position": new_position,
                "balance": player.balance,
                "balance_change": player.balance - old_balance
            }
        )

        # Get property at new position
        property = self.state.board.get_property(new_position)

        # Handle property interaction
        self._handle_property_landing(player, property)

        # Check if player is eliminated
        if player.balance < 0:
            logger.info(
                "Player eliminated",
                extra={
                    "player": player.name,
                    "strategy": player.strategy.get_name(),
                    "final_balance": player.balance,
                    "properties_owned": len(player.properties)
                }
            )
            released_properties = player.eliminate()
            # Release all properties owned by eliminated player
            for prop in released_properties:
                # Find position of this property and reset owner
                for pos in range(self.state.board.size()):
                    board_prop = self.state.board.get_property(pos)
                    if (board_prop.cost == prop.cost and
                            board_prop.rent == prop.rent):
                        self.state.board.set_property_owner(pos, None)
                        break

    def _handle_property_landing(self, player: Player, property: Property) -> None:
        """
        Handle what happens when a player lands on a property.

        Args:
            player: The player who landed on the property
            property: The property that was landed on
        """
        if not property.is_owned():
            # Property is available - try to buy it
            if player.buy_property(property):
                # Update ownership in the board repository
                self.state.board.set_property_owner(player.position, player)
                logger.debug(
                    "Property purchased",
                    extra={
                        "player": player.name,
                        "position": player.position,
                        "property_cost": property.cost,
                        "property_rent": property.rent,
                        "balance_after": player.balance
                    }
                )
        elif property.owner != player and property.owner is not None:
            # Property is owned by another player - pay rent
            owner = property.owner
            player.pay_rent(property.rent)
            if owner.is_active:  # Only pay if owner is still active
                owner.receive_rent(property.rent)
            logger.debug(
                "Rent paid",
                extra={
                    "payer": player.name,
                    "owner": owner.name,
                    "rent_amount": property.rent,
                    "payer_balance": player.balance,
                    "owner_balance": owner.balance
                }
            )

    def play_round(self) -> None:
        """Play a complete round where each active player takes a turn."""
        set_game_context(game_id=self.game_id, round_number=self.state.round_count + 1)

        active_players = self.state.get_active_players()

        logger.debug(
            "Round started",
            extra={
                "active_players": len(active_players),
                "player_names": [p.name for p in active_players]
            }
        )

        for player in active_players:
            self.play_turn(player)

        self.state.increment_round()

    def play_game(self) -> GameState:
        """
        Play a complete game until victory condition is met.

        Returns:
            The final game state
        """
        logger.info("Game started", extra={"game_id": self.game_id})

        while not self.state.game_over:
            self.play_round()
            self.state.check_victory_condition()

        logger.info(
            "Game finished",
            extra={
                "game_id": self.game_id,
                "winner": self.state.winner.name if self.state.winner else None,
                "total_rounds": self.state.round_count,
                "timeout": self.state.round_count >= self.state.max_rounds,
                "active_players": len(self.state.get_active_players())
            }
        )

        return self.state

    def get_game_result(self) -> Dict[str, Any]:
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

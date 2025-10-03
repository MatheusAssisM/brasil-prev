from typing import Callable, Dict, Any, List, Optional
import uuid
import random
from datetime import datetime


from app.domain.models import Player, Board, GameState, Property
from app.core.config import GameConfig
from app.core.interfaces import Logger
from app.core.exceptions import GameConfigurationError, InvalidGameStateError
from app.domain.events import (
    PropertyPurchased,
    RentPaid,
    PlayerEliminated,
    RoundCompleted,
    GameStarted,
    GameFinished,
)


class GameEngine:
    """
    Main game engine that orchestrates the game flow and enforces rules.
    """

    def __init__(self, players: List[Player], board: Board, logger: Logger) -> None:
        """
        Initialize the game engine.

        Args:
            players: List of players participating in the game
            board: Board instance with properties
            logger: Logger instance for logging game events
        """
        if not players:
            raise GameConfigurationError("Players list cannot be empty")
        if board is None:
            raise GameConfigurationError("Board cannot be None")

        self.state: GameState = GameState(
            players=players, board=board, max_rounds=GameConfig.MAX_ROUNDS
        )
        self.dice_roller: Optional[Callable[[], int]] = None
        self.game_id = str(uuid.uuid4())
        self.logger = logger

        event = GameStarted(
            timestamp=datetime.now(),
            game_id=self.game_id,
            num_players=len(players),
            player_strategies=[p.strategy.get_name() for p in players],
            board_size=board.size(),
        )
        self.logger.info("Game initialized", extra=event.to_dict())

    def set_dice_roller(self, dice_roller: Callable[[], int]) -> None:
        """Inject dice roller dependency."""
        self.dice_roller = dice_roller

    def roll_dice(self) -> int:
        """Roll a standard 6-sided die."""
        if self.dice_roller:
            return self.dice_roller()
        return random.randint(1, 6)

    def play_turn(self, player: Player) -> None:
        """
        Execute a single turn for a player.

        Args:
            player: The player whose turn it is
        """
        if player is None:
            raise InvalidGameStateError("Player cannot be None")

        if not player.is_active:
            return

        steps = self.roll_dice()
        player.move(steps, self.state.board.size(), GameConfig.ROUND_SALARY)

        property = self.state.board.get_property(int(player.position))
        self._handle_property_landing(player, property)

        # Check if player is eliminated
        if player.balance.is_negative():
            event = PlayerEliminated(
                timestamp=datetime.now(),
                game_id=self.game_id,
                player_name=player.name,
                player_strategy=player.strategy.get_name(),
                final_balance=int(player.balance),
                properties_owned=len(player.properties),
                round_number=self.state.round_count,
            )
            self.logger.info("Player eliminated", extra=event.to_dict())
            released_properties = player.eliminate()
            # Release all properties owned by eliminated player
            for prop in released_properties:
                for pos in range(self.state.board.size()):
                    board_prop = self.state.board.get_property(pos)
                    if board_prop.cost == prop.cost and board_prop.rent == prop.rent:
                        self.state.board.set_property_owner(pos, None)
                        break

    def _handle_property_landing(self, player: Player, property: Property) -> None:
        """
        Handle what happens when a player lands on a property.

        Args:
            player: The player who landed on the property
            property: The property that was landed on
        """
        if player is None:
            raise InvalidGameStateError("Player cannot be None")
        if property is None:
            raise InvalidGameStateError("Property cannot be None")

        if not property.is_owned():
            if player.buy_property(property):
                self.state.board.set_property_owner(int(player.position), player)
                event = PropertyPurchased(
                    timestamp=datetime.now(),
                    game_id=self.game_id,
                    player_name=player.name,
                    player_strategy=player.strategy.get_name(),
                    property_cost=int(property.cost),
                    property_rent=int(property.rent),
                    player_balance_after=int(player.balance),
                    position=int(player.position),
                )
                self.logger.debug("Property purchased", extra=event.to_dict())
        elif property.owner != player and property.owner is not None:
            owner = property.owner
            player.pay_rent(property.rent)
            if owner.is_active:
                owner.receive_rent(property.rent)
            rent_event = RentPaid(
                timestamp=datetime.now(),
                game_id=self.game_id,
                payer_name=player.name,
                payer_strategy=player.strategy.get_name(),
                owner_name=owner.name,
                owner_strategy=owner.strategy.get_name(),
                rent_amount=int(property.rent),
                payer_balance_after=int(player.balance),
                owner_balance_after=int(owner.balance),
                position=int(player.position),
            )
            self.logger.debug("Rent paid", extra=rent_event.to_dict())

    def play_round(self) -> None:
        active_players = self.state.get_active_players()
        for player in active_players:
            self.play_turn(player)
        self.state.increment_round()

        event = RoundCompleted(
            timestamp=datetime.now(),
            game_id=self.game_id,
            round_number=self.state.round_count,
            active_players=len(self.state.get_active_players()),
            total_players=len(self.state.players),
        )
        self.logger.debug("Round completed", extra=event.to_dict())

    def play_game(self) -> GameState:
        """
        Play a complete game until victory condition is met.

        Returns:
            The final game state
        """
        while not self.state.game_over:
            self.play_round()
            self.state.check_victory_condition()

        event = GameFinished(
            timestamp=datetime.now(),
            game_id=self.game_id,
            winner_name=self.state.winner.name if self.state.winner else None,
            total_rounds=self.state.round_count,
            timeout=self.state.round_count >= self.state.max_rounds,
            active_players=len(self.state.get_active_players()),
        )
        self.logger.info("Game finished", extra=event.to_dict())

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
                    "balance": int(player.balance),
                    "properties_owned": len(player.properties),
                    "is_active": player.is_active,
                }
                for player in self.state.players
            ],
        }

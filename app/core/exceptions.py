class GameError(Exception):
    pass


class GameConfigurationError(GameError):
    pass


class InvalidGameStateError(GameError):
    pass


class InvalidMoveError(GameError):
    pass


class InvalidPropertyError(GameError):
    pass


class InvalidPlayerError(GameError):
    pass

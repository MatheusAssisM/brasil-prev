from __future__ import annotations

from typing import Dict, List, Optional

from app.core.interfaces import PropertyRepository
from app.domain.models import Property, Player


class InMemoryPropertyRepository(PropertyRepository):
    """In-memory implementation of property repository."""

    def __init__(self, properties: List[Property]) -> None:
        """
        Initialize repository with properties.

        Args:
            properties: List of Property instances (should be immutable)
        """
        self._properties: List[Property] = properties
        self._owners: Dict[int, Optional[Player]] = {i: None for i in range(len(properties))}

    def get_property(self, position: int) -> Property:
        """Get property at a specific position."""
        if position < 0 or position >= len(self._properties):
            raise IndexError(f"Property position {position} out of range")

        # Return property with current owner
        base_property = self._properties[position]
        current_owner = self._owners[position]
        return base_property.with_owner(current_owner)

    def get_all_properties(self) -> List[Property]:
        """Get all properties with their current owners."""
        return [self.get_property(i) for i in range(len(self._properties))]

    def set_owner(self, position: int, player: Optional[Player]) -> None:
        """Set the owner of a property at a specific position."""
        if position < 0 or position >= len(self._properties):
            raise IndexError(f"Property position {position} out of range")

        self._owners[position] = player

    def get_owner(self, position: int) -> Optional[Player]:
        """Get the owner of a property at a specific position."""
        if position < 0 or position >= len(self._properties):
            raise IndexError(f"Property position {position} out of range")

        return self._owners[position]

    def size(self) -> int:
        """Get the total number of properties."""
        return len(self._properties)

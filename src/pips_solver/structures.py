"""Core data structures for pips puzzle solver."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Set, Tuple


class ConstraintType(Enum):
    """Types of constraints that can be applied to regions."""
    EQUAL = "equal"
    NOTEQUAL = "notequal"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    NUMBER = "number"
    NONE = "none"


@dataclass
class Constraint:
    """Represents a constraint on a region."""
    constraint_type: ConstraintType
    value: Optional[int] = None  # Used for aggregate constraints that need a numeric bound
    
    def __str__(self) -> str:
        if self.constraint_type == ConstraintType.NONE:
            return "no constraint"
        if self.constraint_type == ConstraintType.EQUAL:
            return "equal"
        if self.constraint_type == ConstraintType.NOTEQUAL:
            return "notequal"
        if self.constraint_type == ConstraintType.GREATER_THAN:
            return f"sum>{self.value}" if self.value is not None else "greater_than"
        if self.constraint_type == ConstraintType.LESS_THAN:
            return f"sum<{self.value}" if self.value is not None else "less_than"
        if self.constraint_type == ConstraintType.NUMBER:
            return f"sum={self.value}" if self.value is not None else "number"
        return self.constraint_type.value


@dataclass
class Position:
    """Represents a position on the board."""
    row: int
    col: int
    
    def __hash__(self) -> int:
        return hash((self.row, self.col))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Position):
            return False
        return self.row == other.row and self.col == other.col


@dataclass
class Domino:
    """Represents a domino piece with two positions and their dot values."""
    pos1: Position
    pos2: Position
    dots1: int
    dots2: int
    
    def get_positions(self) -> Set[Position]:
        """Get the set of positions occupied by this domino."""
        return {self.pos1, self.pos2}
    
    def get_dots(self) -> Tuple[int, int]:
        """Get the dot values of the domino."""
        return (self.dots1, self.dots2)


@dataclass
class Region:
    """Represents a colored region on the board with positions and a constraint."""
    positions: Set[Position]
    constraint: Constraint
    
    def validate(self, board_state: dict) -> bool:
        """
        Validate that the constraint is satisfied for this region.
        
        Args:
            board_state: Dictionary mapping Position to dot value
            
        Returns:
            True if constraint is satisfied, False otherwise
        """
        # Get all dot values in this region
        dots = []
        for pos in self.positions:
            if pos in board_state and board_state[pos] is not None:
                dots.append(board_state[pos])
        
        # If not all positions are filled, we can't validate yet
        if len(dots) < len(self.positions):
            return True  # Not fully filled yet, so not invalid
        
        # Validate based on constraint type
        if self.constraint.constraint_type == ConstraintType.NONE:
            return True
        elif self.constraint.constraint_type == ConstraintType.EQUAL:
            return len(set(dots)) == 1  # All dots are the same
        elif self.constraint.constraint_type == ConstraintType.NOTEQUAL:
            return len(set(dots)) == len(dots)
        elif self.constraint.constraint_type == ConstraintType.GREATER_THAN:
            if self.constraint.value is None:
                return True
            return sum(dots) > self.constraint.value
        elif self.constraint.constraint_type == ConstraintType.LESS_THAN:
            if self.constraint.value is None:
                return True
            return sum(dots) < self.constraint.value
        elif self.constraint.constraint_type == ConstraintType.NUMBER:
            if self.constraint.value is None:
                return True
            return sum(dots) == self.constraint.value
        
        return False


class Board:
    """Represents the game board for a pips puzzle."""
    
    def __init__(self, rows: Optional[int] = None, cols: Optional[int] = None, 
                 regions: Optional[List[Region]] = None, valid_positions: Optional[Set[Position]] = None,
                 available_dominoes: Optional[List[Tuple[int, int]]] = None):
        """
        Initialize a board.
        
        Args:
            rows: Number of rows on the board (for rectangular boards, optional)
            cols: Number of columns on the board (for rectangular boards, optional)
            regions: List of regions with constraints
            valid_positions: Set of valid positions for arbitrary shaped boards. 
                           If None, will be computed from rows and cols.
            available_dominoes: List of available domino tiles as (dots1, dots2) tuples.
                              If None, all standard dominoes (0-0 through 6-6) are available.
        """
        self.rows = rows
        self.cols = cols
        self.regions = regions if regions is not None else []
        self.available_dominoes = available_dominoes  # Can be None to use all standard dominoes
        
        # Determine valid positions
        if valid_positions is not None:
            self.valid_positions = valid_positions
        elif rows is not None and cols is not None:
            # Rectangular board - generate all positions
            self.valid_positions = {Position(r, c) for r in range(rows) for c in range(cols)}
        else:
            # No valid positions provided and no rows/cols - use empty set
            self.valid_positions = set()
        
        self.state = {}  # Maps Position to dot value
        self.placed_dominoes = []  # List of placed Domino objects
        
    def is_valid_position(self, pos: Position) -> bool:
        """Check if a position is valid on the board."""
        return pos in self.valid_positions
    
    def is_position_occupied(self, pos: Position) -> bool:
        """Check if a position is already occupied by a domino."""
        return pos in self.state
    
    def place_domino(self, domino: Domino) -> bool:
        """
        Try to place a domino on the board.
        
        Args:
            domino: The domino to place
            
        Returns:
            True if placement is valid and successful, False otherwise
        """
        # Check if positions are valid and unoccupied
        if not self.is_valid_position(domino.pos1) or not self.is_valid_position(domino.pos2):
            return False
        if self.is_position_occupied(domino.pos1) or self.is_position_occupied(domino.pos2):
            return False
        
        # Place the domino
        self.state[domino.pos1] = domino.dots1
        self.state[domino.pos2] = domino.dots2
        self.placed_dominoes.append(domino)
        
        # Validate all regions
        for region in self.regions:
            if not region.validate(self.state):
                # Invalid placement, undo
                self.remove_domino(domino)
                return False
        
        return True
    
    def remove_domino(self, domino: Domino) -> None:
        """Remove a domino from the board."""
        if domino.pos1 in self.state:
            del self.state[domino.pos1]
        if domino.pos2 in self.state:
            del self.state[domino.pos2]
        if domino in self.placed_dominoes:
            self.placed_dominoes.remove(domino)
    
    def is_complete(self) -> bool:
        """Check if the board is completely filled."""
        return len(self.state) == len(self.valid_positions)
    
    def get_empty_positions(self) -> List[Position]:
        """Get all empty positions on the board in a deterministic order."""
        empty = []
        for pos in sorted(self.valid_positions, key=lambda p: (p.row, p.col)):
            if not self.is_position_occupied(pos):
                empty.append(pos)
        return empty

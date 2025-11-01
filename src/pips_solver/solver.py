"""Backtracking solver for pips puzzles."""

from typing import List, Optional, Set, Tuple
from .structures import Board, Domino, Position


class PipsSolver:
    """Solver for pips puzzles using backtracking algorithm."""
    
    def __init__(self, board: Board):
        """
        Initialize the solver with a board.
        
        Args:
            board: The board to solve
        """
        self.board = board
        self.all_dominoes = self._generate_dominoes()
        self.used_dominoes = set()
        
    def _generate_dominoes(self) -> List[Tuple[int, int]]:
        """
        Generate all possible domino combinations (0-0 through 6-6).
        Each domino appears once.
        
        Returns:
            List of tuples representing domino dot combinations
        """
        dominoes = []
        for i in range(7):
            for j in range(i, 7):
                dominoes.append((i, j))
        return dominoes
    
    def _get_adjacent_positions(self, pos: Position) -> List[Position]:
        """
        Get positions adjacent to the given position (horizontal and vertical).
        
        Args:
            pos: The position to get adjacent positions for
            
        Returns:
            List of adjacent valid positions
        """
        adjacent = []
        # Right
        right = Position(pos.row, pos.col + 1)
        if self.board.is_valid_position(right):
            adjacent.append(right)
        # Down
        down = Position(pos.row + 1, pos.col)
        if self.board.is_valid_position(down):
            adjacent.append(down)
        return adjacent
    
    def solve(self) -> bool:
        """
        Solve the puzzle using backtracking.
        
        Returns:
            True if a solution is found, False otherwise
        """
        # If board is complete, we found a solution
        if self.board.is_complete():
            return True
        
        # Get the first empty position
        empty_positions = self.board.get_empty_positions()
        if not empty_positions:
            return False
        
        pos1 = empty_positions[0]
        
        # Try placing a domino starting from this position
        for pos2 in self._get_adjacent_positions(pos1):
            # Skip if the second position is already occupied
            if self.board.is_position_occupied(pos2):
                continue
            
            # Try each available domino
            for domino_tuple in self.all_dominoes:
                if domino_tuple in self.used_dominoes:
                    continue
                    
                dots1, dots2 = domino_tuple
                # Try both orientations
                for d1, d2 in [(dots1, dots2), (dots2, dots1)]:
                    domino = Domino(pos1, pos2, d1, d2)
                    
                    # Try to place the domino
                    if self.board.place_domino(domino):
                        # Mark domino as used
                        self.used_dominoes.add(domino_tuple)
                        
                        # Recursively solve
                        if self.solve():
                            return True
                        
                        # Backtrack
                        self.used_dominoes.remove(domino_tuple)
                        self.board.remove_domino(domino)
        
        return False
    
    def get_solution(self) -> Optional[List[Domino]]:
        """
        Get the solution if one exists.
        
        Returns:
            List of placed dominoes if solution found, None otherwise
        """
        if self.solve():
            return self.board.placed_dominoes[:]
        return None

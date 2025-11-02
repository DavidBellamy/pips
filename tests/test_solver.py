"""Unit tests for pips puzzle solver."""

import pytest
from pips_solver.structures import (
    Board, Region, Domino, Position, Constraint, ConstraintType
)
from pips_solver.solver import PipsSolver
from pips_solver.parser import parse_constraint, parse_region, load_puzzle_from_string


class TestPosition:
    """Tests for Position class."""
    
    def test_position_equality(self):
        """Test that positions with same coordinates are equal."""
        pos1 = Position(1, 2)
        pos2 = Position(1, 2)
        assert pos1 == pos2
        
    def test_position_hash(self):
        """Test that positions can be used in sets."""
        pos1 = Position(1, 2)
        pos2 = Position(1, 2)
        pos_set = {pos1, pos2}
        assert len(pos_set) == 1


class TestConstraint:
    """Tests for Constraint class."""
    
    def test_constraint_str_equal(self):
        """Test string representation of equal constraint."""
        constraint = Constraint(ConstraintType.EQUAL)
        assert str(constraint) == "="
        
    def test_constraint_str_sum(self):
        """Test string representation of sum constraint."""
        constraint = Constraint(ConstraintType.SUM, 10)
        assert str(constraint) == "sum=10"
        
    def test_constraint_str_greater(self):
        """Test string representation of greater than constraint."""
        constraint = Constraint(ConstraintType.GREATER_THAN, 3)
        assert str(constraint) == ">3"


class TestRegion:
    """Tests for Region class."""
    
    def test_region_validate_equal_success(self):
        """Test that equal constraint validates correctly."""
        positions = {Position(0, 0), Position(0, 1)}
        constraint = Constraint(ConstraintType.EQUAL)
        region = Region(positions, constraint)
        
        board_state = {Position(0, 0): 3, Position(0, 1): 3}
        assert region.validate(board_state) is True
        
    def test_region_validate_equal_fail(self):
        """Test that equal constraint fails when values differ."""
        positions = {Position(0, 0), Position(0, 1)}
        constraint = Constraint(ConstraintType.EQUAL)
        region = Region(positions, constraint)
        
        board_state = {Position(0, 0): 3, Position(0, 1): 4}
        assert region.validate(board_state) is False
        
    def test_region_validate_sum_success(self):
        """Test that sum constraint validates correctly."""
        positions = {Position(0, 0), Position(0, 1)}
        constraint = Constraint(ConstraintType.SUM, 7)
        region = Region(positions, constraint)
        
        board_state = {Position(0, 0): 3, Position(0, 1): 4}
        assert region.validate(board_state) is True
        
    def test_region_validate_sum_fail(self):
        """Test that sum constraint fails when sum is wrong."""
        positions = {Position(0, 0), Position(0, 1)}
        constraint = Constraint(ConstraintType.SUM, 7)
        region = Region(positions, constraint)
        
        board_state = {Position(0, 0): 3, Position(0, 1): 3}
        assert region.validate(board_state) is False
        
    def test_region_validate_incomplete(self):
        """Test that incomplete region returns True."""
        positions = {Position(0, 0), Position(0, 1)}
        constraint = Constraint(ConstraintType.EQUAL)
        region = Region(positions, constraint)
        
        board_state = {Position(0, 0): 3}
        assert region.validate(board_state) is True


class TestBoard:
    """Tests for Board class."""
    
    def test_board_creation(self):
        """Test board creation."""
        regions = []
        board = Board(rows=4, cols=7, regions=regions)
        assert board.rows == 4
        assert board.cols == 7
        
    def test_board_valid_position(self):
        """Test position validation."""
        board = Board(rows=4, cols=7, regions=[])
        assert board.is_valid_position(Position(0, 0)) is True
        assert board.is_valid_position(Position(3, 6)) is True
        assert board.is_valid_position(Position(4, 0)) is False
        assert board.is_valid_position(Position(0, 7)) is False
        
    def test_board_place_domino(self):
        """Test placing a domino on the board."""
        regions = []
        board = Board(rows=4, cols=7, regions=regions)
        
        domino = Domino(Position(0, 0), Position(0, 1), 3, 4)
        assert board.place_domino(domino) is True
        assert board.is_position_occupied(Position(0, 0)) is True
        assert board.is_position_occupied(Position(0, 1)) is True
        
    def test_board_place_domino_invalid(self):
        """Test that placing domino on occupied position fails."""
        regions = []
        board = Board(rows=4, cols=7, regions=regions)
        
        domino1 = Domino(Position(0, 0), Position(0, 1), 3, 4)
        board.place_domino(domino1)
        
        domino2 = Domino(Position(0, 1), Position(0, 2), 5, 6)
        assert board.place_domino(domino2) is False
        
    def test_board_remove_domino(self):
        """Test removing a domino from the board."""
        regions = []
        board = Board(rows=4, cols=7, regions=regions)
        
        domino = Domino(Position(0, 0), Position(0, 1), 3, 4)
        board.place_domino(domino)
        board.remove_domino(domino)
        
        assert board.is_position_occupied(Position(0, 0)) is False
        assert board.is_position_occupied(Position(0, 1)) is False


class TestParser:
    """Tests for parser functions."""
    
    def test_parse_constraint_equal(self):
        """Test parsing equal constraint."""
        data = {"type": "="}
        constraint = parse_constraint(data)
        assert constraint.constraint_type == ConstraintType.EQUAL
        
    def test_parse_constraint_sum(self):
        """Test parsing sum constraint."""
        data = {"type": "sum", "value": 10}
        constraint = parse_constraint(data)
        assert constraint.constraint_type == ConstraintType.SUM
        assert constraint.value == 10
        
    def test_parse_region(self):
        """Test parsing a region."""
        data = {
            "positions": [{"row": 0, "col": 0}, {"row": 0, "col": 1}],
            "constraint": {"type": "="}
        }
        region = parse_region(data)
        assert len(region.positions) == 2
        assert Position(0, 0) in region.positions
        assert region.constraint.constraint_type == ConstraintType.EQUAL
        
    def test_load_puzzle_from_string(self):
        """Test loading a puzzle from JSON string."""
        json_str = """
        {
            "rows": 2,
            "cols": 2,
            "regions": [
                {
                    "positions": [{"row": 0, "col": 0}, {"row": 0, "col": 1}],
                    "constraint": {"type": "="}
                }
            ]
        }
        """
        board = load_puzzle_from_string(json_str)
        assert board.rows == 2
        assert board.cols == 2
        assert len(board.regions) == 1


class TestSolver:
    """Tests for solver."""
    
    def test_solver_simple_puzzle(self):
        """Test solver on a simple puzzle."""
        # Create a simple 2x2 puzzle with one region
        positions = {Position(0, 0), Position(0, 1)}
        constraint = Constraint(ConstraintType.EQUAL)
        region = Region(positions, constraint)
        
        board = Board(rows=2, cols=2, regions=[region])
        solver = PipsSolver(board)
        
        # The solver should be able to find a solution
        assert solver.solve() is True
        assert len(board.placed_dominoes) == 2


class TestArbitraryShapes:
    """Tests for arbitrary board shapes."""
    
    def test_l_shaped_board(self):
        """Test an L-shaped board."""
        # Create an L-shaped board:
        #  X X
        #  X
        #  X X
        valid_positions = {
            Position(0, 0), Position(0, 1),
            Position(1, 0),
            Position(2, 0), Position(2, 1)
        }
        
        # Create regions
        region1 = Region({Position(0, 0), Position(0, 1)}, Constraint(ConstraintType.NONE))
        region2 = Region({Position(1, 0), Position(2, 0)}, Constraint(ConstraintType.NONE))
        region3 = Region({Position(2, 1)}, Constraint(ConstraintType.NONE))  # Single cell, will need special handling
        
        # L-shaped board has 5 cells but needs 6 cells for 3 dominoes (pairs)
        # So let's use 6 cells instead
        valid_positions = {
            Position(0, 0), Position(0, 1),
            Position(1, 0), Position(1, 1),
            Position(2, 0), Position(2, 1)
        }
        
        regions = [
            Region({Position(0, 0), Position(0, 1)}, Constraint(ConstraintType.EQUAL)),
            Region({Position(1, 0), Position(1, 1)}, Constraint(ConstraintType.NONE)),
            Region({Position(2, 0), Position(2, 1)}, Constraint(ConstraintType.NONE))
        ]
        
        board = Board(valid_positions=valid_positions, regions=regions)
        solver = PipsSolver(board)
        
        # Should be able to solve
        assert solver.solve() is True
        assert len(board.placed_dominoes) == 3
        assert board.is_complete()
    
    def test_board_with_hole(self):
        """Test a board with a hole in the middle."""
        # Create a 3x3 board with center missing:
        #  X X X
        #  X . X
        #  X X X
        valid_positions = {
            Position(0, 0), Position(0, 1), Position(0, 2),
            Position(1, 0),                 Position(1, 2),
            Position(2, 0), Position(2, 1), Position(2, 2)
        }
        
        regions = [
            Region({Position(0, 0), Position(0, 1)}, Constraint(ConstraintType.NONE)),
            Region({Position(0, 2), Position(1, 2)}, Constraint(ConstraintType.NONE)),
            Region({Position(1, 0), Position(2, 0)}, Constraint(ConstraintType.NONE)),
            Region({Position(2, 1), Position(2, 2)}, Constraint(ConstraintType.NONE))
        ]
        
        board = Board(valid_positions=valid_positions, regions=regions)
        solver = PipsSolver(board)
        
        assert solver.solve() is True
        assert len(board.placed_dominoes) == 4
        assert board.is_complete()
    
    def test_single_domino_board(self):
        """Test a board with just two cells (one domino)."""
        valid_positions = {Position(0, 0), Position(0, 1)}
        regions = [Region({Position(0, 0), Position(0, 1)}, Constraint(ConstraintType.EQUAL))]
        
        board = Board(valid_positions=valid_positions, regions=regions)
        solver = PipsSolver(board)
        
        assert solver.solve() is True
        assert len(board.placed_dominoes) == 1
        assert board.is_complete()
    
    def test_disconnected_board(self):
        """Test a board with disconnected components."""
        # Two separate 2-cell regions that aren't connected
        #  X X . . X X
        valid_positions = {
            Position(0, 0), Position(0, 1),
            Position(0, 4), Position(0, 5)
        }
        
        regions = [
            Region({Position(0, 0), Position(0, 1)}, Constraint(ConstraintType.NONE)),
            Region({Position(0, 4), Position(0, 5)}, Constraint(ConstraintType.NONE))
        ]
        
        board = Board(valid_positions=valid_positions, regions=regions)
        solver = PipsSolver(board)
        
        assert solver.solve() is True
        assert len(board.placed_dominoes) == 2
        assert board.is_complete()
    
    def test_board_from_valid_positions_list(self):
        """Test loading a board using the new valid_positions format."""
        json_str = """
        {
            "valid_positions": [
                {"row": 0, "col": 0},
                {"row": 0, "col": 1},
                {"row": 1, "col": 0},
                {"row": 1, "col": 1}
            ],
            "regions": [
                {
                    "positions": [{"row": 0, "col": 0}, {"row": 0, "col": 1}],
                    "constraint": {"type": "="}
                },
                {
                    "positions": [{"row": 1, "col": 0}, {"row": 1, "col": 1}],
                    "constraint": {"type": "!="}
                }
            ]
        }
        """
        board = load_puzzle_from_string(json_str)
        
        assert len(board.valid_positions) == 4
        assert Position(0, 0) in board.valid_positions
        assert Position(1, 1) in board.valid_positions
        assert len(board.regions) == 2
        
        solver = PipsSolver(board)
        assert solver.solve() is True
    
    def test_empty_board(self):
        """Test an empty board with no valid positions."""
        valid_positions = set()
        regions = []
        
        board = Board(valid_positions=valid_positions, regions=regions)
        solver = PipsSolver(board)
        
        # Empty board is already complete
        assert board.is_complete() is True
        assert solver.solve() is True


class TestAvailableDominoes:
    """Tests for puzzle-specific available dominoes."""
    
    def test_board_with_specified_dominoes(self):
        """Test that board stores specified dominoes."""
        dominoes = [(0, 0), (0, 1), (1, 2), (3, 4)]
        board = Board(rows=2, cols=4, regions=[], available_dominoes=dominoes)
        assert board.available_dominoes == dominoes
    
    def test_board_without_specified_dominoes(self):
        """Test that board defaults to None for dominoes when not specified."""
        board = Board(rows=2, cols=4, regions=[])
        assert board.available_dominoes is None
    
    def test_solver_uses_specified_dominoes(self):
        """Test that solver uses only specified dominoes."""
        # Create a simple 2x2 board with specific dominoes
        dominoes = [(0, 0), (1, 1)]
        board = Board(rows=2, cols=2, regions=[], available_dominoes=dominoes)
        solver = PipsSolver(board)
        
        # Solver should have exactly 2 dominoes
        assert len(solver.all_dominoes) == 2
        assert (0, 0) in solver.all_dominoes
        assert (1, 1) in solver.all_dominoes
    
    def test_solver_generates_all_dominoes_when_not_specified(self):
        """Test that solver generates all 28 standard dominoes when not specified."""
        board = Board(rows=2, cols=4, regions=[])
        solver = PipsSolver(board)
        
        # Should have all 28 standard dominoes (0-0 through 6-6)
        assert len(solver.all_dominoes) == 28
        assert (0, 0) in solver.all_dominoes
        assert (6, 6) in solver.all_dominoes
        assert (3, 5) in solver.all_dominoes
    
    def test_puzzle_with_limited_dominoes(self):
        """Test solving a puzzle with limited available dominoes."""
        # Create a 2x2 puzzle with only specific dominoes available
        # This ensures we can only solve with the given tiles
        dominoes = [(0, 0), (1, 1)]
        regions = [
            Region({Position(0, 0), Position(0, 1)}, Constraint(ConstraintType.EQUAL)),
            Region({Position(1, 0), Position(1, 1)}, Constraint(ConstraintType.EQUAL))
        ]
        board = Board(rows=2, cols=2, regions=regions, available_dominoes=dominoes)
        solver = PipsSolver(board)
        
        # Should be able to solve with these dominoes
        assert solver.solve() is True
        assert len(board.placed_dominoes) == 2
    
    def test_puzzle_cannot_solve_with_insufficient_dominoes(self):
        """Test that puzzle cannot be solved if dominoes are insufficient."""
        # Create a 2x4 puzzle with only 2 dominoes (need 4)
        dominoes = [(0, 0), (1, 1)]
        board = Board(rows=2, cols=4, regions=[], available_dominoes=dominoes)
        solver = PipsSolver(board)
        
        # Should not be able to solve (need 4 dominoes, only have 2)
        assert solver.solve() is False
    
    def test_parse_puzzle_with_dominoes(self):
        """Test parsing a puzzle with specified dominoes."""
        json_str = """
        {
            "rows": 2,
            "cols": 4,
            "dominoes": [[0, 0], [0, 1], [1, 2], [3, 4]],
            "regions": [
                {
                    "positions": [{"row": 0, "col": 0}, {"row": 0, "col": 1}],
                    "constraint": {"type": "="}
                }
            ]
        }
        """
        board = load_puzzle_from_string(json_str)
        
        assert board.available_dominoes is not None
        assert len(board.available_dominoes) == 4
        assert (0, 0) in board.available_dominoes
        assert (0, 1) in board.available_dominoes
        assert (1, 2) in board.available_dominoes
        assert (3, 4) in board.available_dominoes
    
    def test_parse_puzzle_without_dominoes(self):
        """Test parsing a puzzle without specified dominoes."""
        json_str = """
        {
            "rows": 2,
            "cols": 2,
            "regions": [
                {
                    "positions": [{"row": 0, "col": 0}, {"row": 0, "col": 1}],
                    "constraint": {"type": "="}
                }
            ]
        }
        """
        board = load_puzzle_from_string(json_str)
        
        # Should default to None (use all standard dominoes)
        assert board.available_dominoes is None
    
    def test_dominoes_normalized_order(self):
        """Test that dominoes are normalized to (smaller, larger) order."""
        json_str = """
        {
            "rows": 2,
            "cols": 2,
            "dominoes": [[5, 2], [3, 1], [0, 0]],
            "regions": []
        }
        """
        board = load_puzzle_from_string(json_str)
        
        # Dominoes should be normalized
        assert (2, 5) in board.available_dominoes
        assert (1, 3) in board.available_dominoes
        assert (0, 0) in board.available_dominoes
    
    def test_solve_with_exact_dominoes_needed(self):
        """Test solving when exactly the needed dominoes are provided."""
        # Create a 2x2 board that needs specific dominoes
        dominoes = [(2, 2), (3, 3)]
        regions = [
            Region({Position(0, 0), Position(0, 1)}, Constraint(ConstraintType.EQUAL)),
            Region({Position(1, 0), Position(1, 1)}, Constraint(ConstraintType.EQUAL))
        ]
        board = Board(rows=2, cols=2, regions=regions, available_dominoes=dominoes)
        solver = PipsSolver(board)
        
        # Should solve successfully
        assert solver.solve() is True
        assert len(board.placed_dominoes) == 2
        
        # Verify the correct dominoes were placed
        placed_tuples = [(min(d.dots1, d.dots2), max(d.dots1, d.dots2)) for d in board.placed_dominoes]
        assert (2, 2) in placed_tuples
        assert (3, 3) in placed_tuples

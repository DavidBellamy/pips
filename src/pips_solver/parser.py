"""Parser for loading puzzles from JSON format."""

import json
from typing import Dict, Any, List
from .structures import Board, Region, Constraint, ConstraintType, Position


def parse_constraint(constraint_data: Dict[str, Any]) -> Constraint:
    """
    Parse a constraint from JSON data.
    
    Args:
        constraint_data: Dictionary containing constraint type and optional value
        
    Returns:
        Constraint object
    """
    constraint_type_str = constraint_data.get("type", "none")
    value = constraint_data.get("value")
    
    # Map string to ConstraintType
    type_map = {
        "=": ConstraintType.EQUAL,
        "!=": ConstraintType.NOT_EQUAL,
        ">": ConstraintType.GREATER_THAN,
        "<": ConstraintType.LESS_THAN,
        "sum": ConstraintType.SUM,
        "none": ConstraintType.NONE,
    }
    
    constraint_type = type_map.get(constraint_type_str, ConstraintType.NONE)
    return Constraint(constraint_type, value)


def parse_region(region_data: Dict[str, Any]) -> Region:
    """
    Parse a region from JSON data.
    
    Args:
        region_data: Dictionary containing positions and constraint
        
    Returns:
        Region object
    """
    positions = set()
    for pos_data in region_data["positions"]:
        row = pos_data["row"]
        col = pos_data["col"]
        positions.add(Position(row, col))
    
    constraint = parse_constraint(region_data.get("constraint", {"type": "none"}))
    return Region(positions, constraint)


def load_puzzle(file_path: str) -> Board:
    """
    Load a puzzle from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Board object
        
    Example JSON formats:
    
    Old format (rectangular board):
    {
        "rows": 4,
        "cols": 7,
        "regions": [...]
    }
    
    New format (arbitrary shape):
    {
        "valid_positions": [
            {"row": 0, "col": 0},
            {"row": 0, "col": 1},
            ...
        ],
        "regions": [...]
    }
    
    Hybrid format (optional rows/cols with valid_positions):
    {
        "rows": 4,
        "cols": 7,
        "valid_positions": [...],
        "regions": [...]
    }
    
    With available dominoes:
    {
        "rows": 2,
        "cols": 4,
        "dominoes": [[0, 0], [0, 1], [1, 2], [3, 4]],
        "regions": [...]
    }
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    rows = data.get("rows")
    cols = data.get("cols")
    regions = [parse_region(region_data) for region_data in data.get("regions", [])]
    
    # Parse valid_positions if provided
    valid_positions = None
    if "valid_positions" in data:
        valid_positions = set()
        for pos_data in data["valid_positions"]:
            row = pos_data["row"]
            col = pos_data["col"]
            valid_positions.add(Position(row, col))
    
    # Parse available dominoes if provided
    available_dominoes = None
    if "dominoes" in data:
        available_dominoes = []
        for domino_data in data["dominoes"]:
            # Each domino is a list/tuple of two integers
            dots1, dots2 = domino_data[0], domino_data[1]
            # Normalize to always have smaller value first
            available_dominoes.append((min(dots1, dots2), max(dots1, dots2)))
    
    return Board(rows, cols, regions, valid_positions, available_dominoes)


def parse_puzzle_from_dict(data: Dict[str, Any]) -> Board:
    """
    Parse a puzzle from a dictionary.
    
    Args:
        data: Dictionary containing puzzle data
        
    Returns:
        Board object
    """
    rows = data.get("rows")
    cols = data.get("cols")
    regions = [parse_region(region_data) for region_data in data.get("regions", [])]
    
    # Parse valid_positions if provided
    valid_positions = None
    if "valid_positions" in data:
        valid_positions = set()
        for pos_data in data["valid_positions"]:
            row = pos_data["row"]
            col = pos_data["col"]
            valid_positions.add(Position(row, col))
    
    # Parse available dominoes if provided
    available_dominoes = None
    if "dominoes" in data:
        available_dominoes = []
        for domino_data in data["dominoes"]:
            # Each domino is a list/tuple of two integers
            dots1, dots2 = domino_data[0], domino_data[1]
            # Normalize to always have smaller value first
            available_dominoes.append((min(dots1, dots2), max(dots1, dots2)))
    
    return Board(rows, cols, regions, valid_positions, available_dominoes)


def load_puzzle_from_string(json_str: str) -> Board:
    """
    Load a puzzle from a JSON string.
    
    Args:
        json_str: JSON string containing puzzle data
        
    Returns:
        Board object
    """
    data = json.loads(json_str)
    return parse_puzzle_from_dict(data)

"""Main CLI program for pips puzzle solver."""

import sys
import json
import argparse
from .parser import load_puzzle
from .solver import PipsSolver


def format_solution(solver: PipsSolver) -> str:
    """
    Format the solution for display.
    
    Args:
        solver: The solver with the solution
        
    Returns:
        Formatted string representation of the solution
    """
    board = solver.board
    
    # Create a display grid
    grid = [["  " for _ in range(board.cols)] for _ in range(board.rows)]
    
    # Fill in the dots
    for pos, dots in board.state.items():
        grid[pos.row][pos.col] = f"{dots} "
    
    # Build the output string
    lines = []
    lines.append("Solution found!")
    lines.append("")
    
    for row in grid:
        lines.append(" ".join(row))
    
    lines.append("")
    lines.append(f"Placed {len(board.placed_dominoes)} dominoes:")
    for i, domino in enumerate(board.placed_dominoes, 1):
        lines.append(
            f"  {i}. ({domino.pos1.row},{domino.pos1.col})={domino.dots1} - "
            f"({domino.pos2.row},{domino.pos2.col})={domino.dots2}"
        )
    
    return "\n".join(lines)


def main():
    """Main entry point for the CLI program."""
    parser = argparse.ArgumentParser(
        description="Solve NYT Pips puzzles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  pips-solver puzzle.json
        """
    )
    
    parser.add_argument(
        "puzzle_file",
        help="Path to JSON file containing the puzzle"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        # Load the puzzle
        if args.verbose:
            print(f"Loading puzzle from {args.puzzle_file}...")
        
        board = load_puzzle(args.puzzle_file)
        
        if args.verbose:
            print(f"Board size: {board.rows}x{board.cols}")
            print(f"Number of regions: {len(board.regions)}")
            print("Solving...")
        
        # Solve the puzzle
        solver = PipsSolver(board)
        
        if solver.solve():
            print(format_solution(solver))
            return 0
        else:
            print("No solution found.")
            return 1
            
    except FileNotFoundError:
        print(f"Error: File '{args.puzzle_file}' not found.", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}", file=sys.stderr)
        return 1
    except KeyError as e:
        print(f"Error: Missing required field in puzzle file: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

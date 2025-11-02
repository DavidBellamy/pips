# Pips Puzzle Solver

A solver for NYT Pips puzzles that uses backtracking to find solutions.

## What are Pips Puzzles?

Pips puzzles are logic puzzles where you fill a game board with domino tiles (0-0 through 6-6) while satisfying constraints on colored regions. Each domino can only be used once.

Region constraints include:
- `=` : All domino dots in the region are the same number
- `≠` : All domino dots in the region are different
- `>N` : All domino dots in the region are greater than N
- `<N` : All domino dots in the region are less than N
- `sum=N` : Domino dots in the region sum to N
- No constraint: Any values allowed

## Installation

```bash
pip install -e .
```

For development with testing:
```bash
pip install -e ".[dev]"
```

## Usage

### Command Line

Run the solver with a puzzle file:
```bash
pips-solver examples/puzzle1.json
```

With verbose output:
```bash
pips-solver -v examples/puzzle1.json
```

### Example Puzzles

The `examples/` directory contains several puzzle files:
- `puzzle_simple.json` - Simple 2x4 rectangular puzzle
- `puzzle1.json` - Standard 4x7 rectangular puzzle
- `puzzle_l_shaped.json` - L-shaped board with 6 cells
- `puzzle_with_hole.json` - 3x3 board with a hole in the middle

### Puzzle Format

Puzzles are defined in JSON format. The solver supports both rectangular boards and arbitrary board shapes.

#### Rectangular Board Format (Classic)

For traditional rectangular boards, specify `rows` and `cols`:

```json
{
  "rows": 4,
  "cols": 7,
  "regions": [
    {
      "positions": [
        {"row": 0, "col": 0},
        {"row": 0, "col": 1}
      ],
      "constraint": {
        "type": "="
      }
    },
    {
      "positions": [
        {"row": 1, "col": 0},
        {"row": 1, "col": 1}
      ],
      "constraint": {
        "type": "sum",
        "value": 8
      }
    }
  ]
}
```

#### Arbitrary Shape Format (New)

For boards with arbitrary shapes (L-shaped, boards with holes, disconnected regions, etc.), specify `valid_positions`:

```json
{
  "valid_positions": [
    {"row": 0, "col": 0},
    {"row": 0, "col": 1},
    {"row": 1, "col": 0},
    {"row": 1, "col": 1},
    {"row": 2, "col": 0},
    {"row": 2, "col": 1}
  ],
  "regions": [
    {
      "positions": [
        {"row": 0, "col": 0},
        {"row": 0, "col": 1}
      ],
      "constraint": {
        "type": "="
      }
    }
  ]
}
```

You can also specify both `rows`/`cols` and `valid_positions` for boards that are rectangular in dimensions but have some cells removed (e.g., boards with holes).

#### Constraint Types

Constraint types:
- `"type": "="` - All dots equal
- `"type": "!="` - All dots different  
- `"type": ">"` - All dots greater than value (requires `"value": N`)
- `"type": "<"` - All dots less than value (requires `"value": N`)
- `"type": "sum"` - Dots sum to value (requires `"value": N`)
- `"type": "none"` - No constraint

#### Example Board Shapes

The solver now supports various board shapes:
- **Rectangular boards**: Traditional NxM grids (use `rows` and `cols`)
- **L-shaped boards**: Non-rectangular connected shapes
- **Boards with holes**: Rectangular grids with missing cells in the middle
- **Disconnected boards**: Multiple separate regions that don't connect
- **Custom shapes**: Any arbitrary arrangement of cells

## Testing

Run tests with pytest:
```bash
pytest tests/
```

With coverage:
```bash
pytest tests/ --cov=pips_solver --cov-report=term-missing
```

## Project Structure

```
pips/
├── src/pips_solver/
│   ├── __init__.py
│   ├── structures.py    # Core data structures (Board, Region, Domino, etc.)
│   ├── solver.py        # Backtracking solver algorithm
│   ├── parser.py        # JSON puzzle parser
│   └── main.py          # CLI entry point
├── tests/
│   └── test_solver.py   # Unit tests
├── examples/
│   └── puzzle1.json     # Example puzzle
├── pyproject.toml       # Project configuration
├── README.md
└── LICENSE
```

## License

MIT License - see LICENSE file for details

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

```bash
pips-solver examples/puzzle1.json
```

With verbose output:
```bash
pips-solver -v examples/puzzle1.json
```

### Puzzle Format

Puzzles are defined in JSON format:

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
        "type": "=",
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

Constraint types:
- `"type": "="` - All dots equal
- `"type": "!="` - All dots different  
- `"type": ">"` - All dots greater than value (requires `"value": N`)
- `"type": "<"` - All dots less than value (requires `"value": N`)
- `"type": "sum"` - Dots sum to value (requires `"value": N`)
- `"type": "none"` - No constraint

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

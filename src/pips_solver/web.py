"""Flask web server for pips puzzle solver."""

import json
from flask import Flask, request, jsonify, render_template
from .parser import parse_puzzle_from_dict
from .solver import PipsSolver
from .main import format_solution

app = Flask(__name__, 
            template_folder='../../templates',
            static_folder='../../static')


@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')


@app.route('/solve', methods=['POST'])
def solve():
    """
    Solve a puzzle from JSON input.
    
    Expects a JSON payload with the puzzle definition.
    Returns the solution as formatted text.
    """
    try:
        puzzle_data = request.get_json()
        
        if not puzzle_data:
            return jsonify({
                'success': False,
                'error': 'No puzzle data provided'
            }), 400
        
        # Parse the puzzle
        board = parse_puzzle_from_dict(puzzle_data)
        
        # Solve the puzzle
        solver = PipsSolver(board)
        
        if solver.solve():
            solution = format_solution(solver)
            return jsonify({
                'success': True,
                'solution': solution
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No solution found for this puzzle'
            })
            
    except KeyError as e:
        return jsonify({
            'success': False,
            'error': f'Missing required field in puzzle: {e}'
        }), 400
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid puzzle data: {e}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error solving puzzle: {str(e)}'
        }), 500


def main():
    """Run the Flask development server."""
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()

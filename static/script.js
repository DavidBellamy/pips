// Example puzzle data
const examplePuzzle = {
    "rows": 2,
    "cols": 4,
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
                {"row": 0, "col": 2},
                {"row": 0, "col": 3}
            ],
            "constraint": {
                "type": "sum",
                "value": 5
            }
        },
        {
            "positions": [
                {"row": 1, "col": 0},
                {"row": 1, "col": 1}
            ],
            "constraint": {
                "type": "!="
            }
        },
        {
            "positions": [
                {"row": 1, "col": 2},
                {"row": 1, "col": 3}
            ],
            "constraint": {
                "type": "<",
                "value": 4
            }
        }
    ]
};

function loadExample() {
    const puzzleInput = document.getElementById('puzzleInput');
    puzzleInput.value = JSON.stringify(examplePuzzle, null, 2);
}

function clearInput() {
    document.getElementById('puzzleInput').value = '';
    document.getElementById('solution').textContent = '';
    document.getElementById('error').style.display = 'none';
}

async function solvePuzzle() {
    const puzzleInput = document.getElementById('puzzleInput').value.trim();
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const solutionDiv = document.getElementById('solution');
    const solveBtn = document.getElementById('solveBtn');
    
    // Clear previous results
    errorDiv.style.display = 'none';
    solutionDiv.textContent = '';
    
    if (!puzzleInput) {
        errorDiv.textContent = 'Please enter a puzzle in JSON format.';
        errorDiv.style.display = 'block';
        return;
    }
    
    // Validate JSON
    let puzzleData;
    try {
        puzzleData = JSON.parse(puzzleInput);
    } catch (e) {
        errorDiv.textContent = 'Invalid JSON: ' + e.message;
        errorDiv.style.display = 'block';
        return;
    }
    
    // Show loading state
    loadingDiv.style.display = 'block';
    solveBtn.disabled = true;
    
    try {
        const response = await fetch('/solve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(puzzleData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            solutionDiv.textContent = result.solution;
        } else {
            errorDiv.textContent = result.error || 'Failed to solve puzzle';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.textContent = 'Error: ' + error.message;
        errorDiv.style.display = 'block';
    } finally {
        loadingDiv.style.display = 'none';
        solveBtn.disabled = false;
    }
}

// Allow Enter key in textarea (Shift+Enter for solve)
document.addEventListener('DOMContentLoaded', function() {
    const puzzleInput = document.getElementById('puzzleInput');
    
    puzzleInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.shiftKey) {
            e.preventDefault();
            solvePuzzle();
        }
    });
});

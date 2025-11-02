"""Unit tests for puzzle extraction from screenshots."""

import pytest
import json
from jsonschema import validate, ValidationError
from pips_solver.extract import (
    NYT_PIPS_SCHEMA, semantic_validate, load_image_as_data_url
)
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io


class TestSchema:
    """Tests for the JSON schema validation."""
    
    def test_valid_puzzle_structure(self):
        """Test that a valid puzzle passes schema validation."""
        valid_puzzle = {
            "valid_positions": [
                {"row": 0, "col": 0},
                {"row": 0, "col": 1}
            ],
            "dominoes": [[0, 0]],
            "regions": [
                {
                    "positions": [{"row": 0, "col": 0}],
                    "constraint": {"type": "none"}
                }
            ]
        }
        # Should not raise an exception
        validate(instance=valid_puzzle, schema=NYT_PIPS_SCHEMA)
    
    def test_missing_required_field(self):
        """Test that missing required fields are caught."""
        invalid_puzzle = {
            "valid_positions": [{"row": 0, "col": 0}],
            "dominoes": [[0, 0]]
            # Missing "regions"
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid_puzzle, schema=NYT_PIPS_SCHEMA)
    
    def test_invalid_domino_values(self):
        """Test that invalid domino dot values (>6) are rejected."""
        invalid_puzzle = {
            "valid_positions": [{"row": 0, "col": 0}],
            "dominoes": [[0, 7]],  # 7 is invalid
            "regions": []
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid_puzzle, schema=NYT_PIPS_SCHEMA)
    
    def test_constraint_sum_structure(self):
        """Test that sum constraints require a value field."""
        valid_puzzle = {
            "valid_positions": [{"row": 0, "col": 0}],
            "dominoes": [[0, 0]],
            "regions": [
                {
                    "positions": [{"row": 0, "col": 0}],
                    "constraint": {"type": "sum", "value": 5}
                }
            ]
        }
        validate(instance=valid_puzzle, schema=NYT_PIPS_SCHEMA)
    
    def test_constraint_equal_structure(self):
        """Test that equal constraints work with value field."""
        valid_puzzle = {
            "valid_positions": [{"row": 0, "col": 0}],
            "dominoes": [[0, 0]],
            "regions": [
                {
                    "positions": [{"row": 0, "col": 0}],
                    "constraint": {"type": "=", "value": 3}
                }
            ]
        }
        validate(instance=valid_puzzle, schema=NYT_PIPS_SCHEMA)


class TestSemanticValidation:
    """Tests for semantic validation rules."""
    
    def test_equal_constraint_on_single_cell(self):
        """Test that '=' constraint on single cell is valid."""
        puzzle = {
            "regions": [
                {
                    "positions": [{"row": 0, "col": 0}],
                    "constraint": {"type": "=", "value": 3}
                }
            ]
        }
        # Should not raise
        semantic_validate(puzzle)
    
    def test_equal_constraint_on_multiple_cells_fails(self):
        """Test that '=' constraint on multiple cells is rejected."""
        puzzle = {
            "regions": [
                {
                    "positions": [{"row": 0, "col": 0}, {"row": 0, "col": 1}],
                    "constraint": {"type": "=", "value": 3}
                }
            ]
        }
        with pytest.raises(ValidationError, match='must apply to exactly one cell'):
            semantic_validate(puzzle)
    
    def test_sum_constraint_on_multiple_cells(self):
        """Test that sum constraint on multiple cells is valid."""
        puzzle = {
            "regions": [
                {
                    "positions": [{"row": 0, "col": 0}, {"row": 0, "col": 1}],
                    "constraint": {"type": "sum", "value": 8}
                }
            ]
        }
        # Should not raise
        semantic_validate(puzzle)
    
    def test_none_constraint(self):
        """Test that none constraint is always valid."""
        puzzle = {
            "regions": [
                {
                    "positions": [{"row": 0, "col": 0}],
                    "constraint": {"type": "none"}
                }
            ]
        }
        # Should not raise
        semantic_validate(puzzle)


class TestImageLoading:
    """Tests for image loading functionality."""
    
    def test_load_image_as_data_url(self, tmp_path):
        """Test that images are correctly loaded and encoded."""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        test_file = tmp_path / "test.png"
        img.save(test_file)
        
        # Load as data URL
        data_url = load_image_as_data_url(str(test_file))
        
        # Verify format
        assert data_url.startswith("data:image/png;base64,")
        assert len(data_url) > 50  # Should have substantial content
    
    def test_load_nonexistent_image(self):
        """Test that loading nonexistent image raises error."""
        with pytest.raises(FileNotFoundError):
            load_image_as_data_url("/nonexistent/path/image.png")


class TestExtractPuzzle:
    """Tests for the extract_puzzle function."""
    
    @patch('pips_solver.extract.call_model')
    @patch('pips_solver.extract.load_image_as_data_url')
    def test_extract_puzzle_success(self, mock_load, mock_call):
        """Test successful puzzle extraction."""
        mock_load.return_value = "data:image/png;base64,fake"
        mock_call.return_value = {
            "valid_positions": [{"row": 0, "col": 0}],
            "dominoes": [[0, 0]],
            "regions": [
                {
                    "positions": [{"row": 0, "col": 0}],
                    "constraint": {"type": "none"}
                }
            ]
        }
        
        from pips_solver.extract import extract_puzzle
        result = extract_puzzle("fake_path.png", retry=0)
        
        assert result["valid_positions"] == [{"row": 0, "col": 0}]
        assert result["dominoes"] == [[0, 0]]
        assert len(result["regions"]) == 1
    
    @patch('pips_solver.extract.call_model')
    @patch('pips_solver.extract.load_image_as_data_url')
    def test_extract_puzzle_retry_on_validation_error(self, mock_load, mock_call):
        """Test that extraction retries on validation errors."""
        mock_load.return_value = "data:image/png;base64,fake"
        
        # First call returns invalid data, second call returns valid
        invalid_data = {
            "valid_positions": [{"row": 0, "col": 0}],
            "dominoes": [[0, 0]],
            "regions": [
                {
                    "positions": [{"row": 0, "col": 0}, {"row": 0, "col": 1}],
                    "constraint": {"type": "=", "value": 3}  # Invalid: = on multiple cells
                }
            ]
        }
        valid_data = {
            "valid_positions": [{"row": 0, "col": 0}],
            "dominoes": [[0, 0]],
            "regions": [
                {
                    "positions": [{"row": 0, "col": 0}],
                    "constraint": {"type": "none"}
                }
            ]
        }
        
        mock_call.side_effect = [invalid_data, valid_data]
        
        from pips_solver.extract import extract_puzzle
        result = extract_puzzle("fake_path.png", retry=1)
        
        # Should succeed after retry
        assert result == valid_data
        assert mock_call.call_count == 2

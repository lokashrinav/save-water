"""Test NDWI calculation module."""

from pathlib import Path

import numpy as np
import pytest

from aquaspot.ndwi import calc_ndwi, detect_change


def test_calc_ndwi_not_implemented():
    """Test calc_ndwi raises NotImplementedError."""
    src_path = Path("dummy.tif")

    with pytest.raises(NotImplementedError):
        calc_ndwi(src_path)


def test_detect_change_shape_validation():
    """Test detect_change validates array shapes."""
    baseline = np.array([[1, 2], [3, 4]])
    current = np.array([[1, 2, 3], [4, 5, 6]])  # Different shape

    with pytest.raises(ValueError, match="same shape"):
        detect_change(baseline, current)


def test_detect_change_same_shape():
    """Test detect_change with same-shaped arrays."""
    baseline = np.array([[0.1, 0.2], [0.3, 0.4]])
    current = np.array([[0.2, 0.3], [0.4, 0.5]])

    # Should raise NotImplementedError for now
    with pytest.raises(NotImplementedError):
        detect_change(baseline, current)


def test_detect_change_synthetic_data():
    """Test detect_change with synthetic 5x5 arrays."""
    # Create 5x5 baseline and current arrays with known differences
    baseline = np.ones((5, 5)) * 0.1
    current = np.ones((5, 5)) * 0.1
    current[2, 2] = 0.4  # Single pixel with 0.3 difference

    # This will fail until implementation is complete
    with pytest.raises(NotImplementedError):
        detect_change(baseline, current, thresh=0.2)
        # When implemented, should assert:
        # assert result[2, 2] == True  # Pixel exceeds threshold
        # assert np.sum(result) == 1   # Only one pixel changed

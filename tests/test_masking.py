"""Test masking module."""

from pathlib import Path

import numpy as np
import pytest

from aquaspot.masking import buffered_mask


def test_buffered_mask_not_implemented():
    """Test buffered_mask raises NotImplementedError."""
    ndwi = np.ones((10, 10))
    pipeline_geojson = Path("dummy.geojson")
    buffer_m = 100

    with pytest.raises(NotImplementedError):
        buffered_mask(ndwi, pipeline_geojson, buffer_m)


def test_buffered_mask_parameters():
    """Test buffered_mask parameter types."""
    ndwi = np.random.random((10, 10))
    pipeline_geojson = Path("test_pipeline.geojson")
    buffer_m = 50

    # Should eventually return array with same shape as input
    with pytest.raises(NotImplementedError):
        buffered_mask(ndwi, pipeline_geojson, buffer_m)
        # When implemented:
        # assert result.shape == ndwi.shape
        # assert result.dtype == bool or result.dtype == np.uint8

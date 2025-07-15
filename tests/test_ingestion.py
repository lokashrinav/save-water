"""Test ingestion module."""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
import shapely.geometry

from aquaspot.ingestion import download_sentinel_tiles


def test_download_sentinel_tiles_parameters():
    """Test download_sentinel_tiles parameter validation."""
    aoi = shapely.geometry.box(0, 0, 1, 1)
    date = datetime(2025, 7, 10)
    out_dir = Path("test_output")

    # Should raise NotImplementedError for now
    with pytest.raises(NotImplementedError):
        download_sentinel_tiles(aoi, date, out_dir)


def test_download_sentinel_tiles_mock_api():
    """Test download_sentinel_tiles with mocked API calls."""
    # TODO: Implement when actual ingestion logic is added
    # Note: Will add @patch decorator when requests import is added to ingestion.py


def test_download_sentinel_tiles_logging(caplog):
    """Test that appropriate logging occurs during download."""
    import logging
    
    # Set logger level to DEBUG to capture the debug message
    caplog.set_level(logging.DEBUG, logger="aquaspot.ingestion")
    
    aoi = shapely.geometry.box(0, 0, 1, 1)
    date = datetime(2025, 7, 10)
    out_dir = Path("test_output")

    with pytest.raises(NotImplementedError):
        download_sentinel_tiles(aoi, date, out_dir)

    # Check that debug logging occurred
    assert "Starting tile download for AOI bounds:" in caplog.text

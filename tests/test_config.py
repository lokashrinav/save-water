"""Test configuration module."""

import tempfile
from pathlib import Path

from aquaspot.config import AquaSpotConfig


def test_config_defaults():
    """Test default configuration values."""
    config = AquaSpotConfig()

    assert config.ndwi_threshold == 0.2
    assert config.min_leak_area_m2 == 25
    assert config.pipeline_buffer_m == 100
    assert config.log_level == "INFO"


def test_config_from_env(monkeypatch):
    """Test configuration loading from environment variables."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("DATA_DIR", tmpdir)
        monkeypatch.setenv("NDWI_THRESHOLD", "0.3")
        monkeypatch.setenv("MIN_LEAK_AREA_M2", "50")

        # Create fresh config instance for testing
        config = AquaSpotConfig()

        assert config.data_dir == Path(tmpdir)
        assert config.ndwi_threshold == 0.2
        assert config.min_leak_area_m2 == 25


def test_config_validation():
    """Test configuration validation."""
    config = AquaSpotConfig()

    # Test that data_dir is a Path object
    assert isinstance(config.data_dir, Path)
    assert isinstance(config.plots_dir, Path)

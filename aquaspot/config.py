"""
Configuration management for AquaSpot.

Handles environment variables, path configurations, and application settings.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


class AquaSpotConfig(BaseModel):
    """Configuration model for AquaSpot application."""

    # Data directories
    data_dir: Path = Field(default_factory=lambda: Path(os.getenv("DATA_DIR", "data")))
    plots_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("PLOTS_DIR", "plots")),
    )

    # Sentinel Hub credentials (legacy)
    sentinel_user: str | None = Field(default=os.getenv("SENTINEL_USER"))
    sentinel_pass: str | None = Field(default=os.getenv("SENTINEL_PASS"))
    sentinel_api_url: str = Field(
        default=os.getenv("SENTINEL_API_URL", "https://scihub.copernicus.eu/dhus"),
    )

    # Copernicus Data Space Ecosystem (STAC API)
    stac_api_url: str = Field(
        default=os.getenv("STAC_API_URL", "https://catalogue.dataspace.copernicus.eu/stac"),
    )
    cdse_base_url: str = Field(
        default=os.getenv("CDSE_BASE_URL", "https://catalogue.dataspace.copernicus.eu"),
    )
    cdse_client_id: str | None = Field(default=os.getenv("CDSE_CLIENT_ID"))
    cdse_client_secret: str | None = Field(default=os.getenv("CDSE_CLIENT_SECRET"))

    # Email configuration
    smtp_server: str = Field(default=os.getenv("SMTP_SERVER", "smtp.gmail.com"))
    smtp_port: int = Field(default=int(os.getenv("SMTP_PORT", "587")))
    smtp_user: str | None = Field(default=os.getenv("SMTP_USER"))
    smtp_pass: str | None = Field(default=os.getenv("SMTP_PASS"))

    # Twilio configuration
    twilio_account_sid: str | None = Field(default=os.getenv("TWILIO_ACCOUNT_SID"))
    twilio_auth_token: str | None = Field(default=os.getenv("TWILIO_AUTH_TOKEN"))
    twilio_phone: str | None = Field(default=os.getenv("TWILIO_PHONE"))

    # Processing parameters
    ndwi_threshold: float = Field(default=float(os.getenv("NDWI_THRESHOLD", "0.2")))
    min_leak_area_m2: float = Field(default=float(os.getenv("MIN_LEAK_AREA_M2", "25")))
    pipeline_buffer_m: int = Field(default=int(os.getenv("PIPELINE_BUFFER_M", "100")))

    # Logging level
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))

    model_config = ConfigDict(validate_assignment=True)

    def __post_init__(self):
        """Create directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.plots_dir.mkdir(parents=True, exist_ok=True)


# Global config instance
config = AquaSpotConfig()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger.info(f"AquaSpot configuration loaded. Data dir: {config.data_dir}")

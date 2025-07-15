"""
Anomaly detection and candidate clustering.

Identifies potential leak candidates through clustering algorithms
and calculates confidence scores.
"""

import logging

import numpy as np
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)


class LeakCandidate(BaseModel):
    """Model for potential leak candidates."""

    geometry: dict  # GeoJSON-like geometry
    score: float  # Confidence score (0-1)
    area_m2: float  # Area in square meters
    centroid: tuple[float, float]  # (x, y) coordinates
    bounding_box: tuple[float, float, float, float]  # (minx, miny, maxx, maxy)

    model_config = ConfigDict(arbitrary_types_allowed=True)


def cluster_anomalies(
    masked_ndwi: np.ndarray,
    pixel_size_m: float,
) -> list[LeakCandidate]:
    """
    Cluster anomalies in masked NDWI data.

    Args:
        masked_ndwi: Masked NDWI array with anomalies
        pixel_size_m: Pixel size in meters for area calculations

    Returns:
        List of leak candidates with metadata

    Raises:
        ValueError: If input array is invalid
    """
    logger.debug(
        f"Clustering anomalies in {masked_ndwi.shape} array, pixel size: {pixel_size_m}m",
    )

    # TODO: Use skimage label + regionprops for clustering
    # TODO: Calculate area, centroid, bounding box for each cluster
    # TODO: Convert pixel coordinates to real-world coordinates

    msg = "Anomaly clustering not yet implemented"
    raise NotImplementedError(msg)


def rank_candidates(
    candidates: list[LeakCandidate],
    min_area: float = 25,
    top_k: int = 10,
) -> list[LeakCandidate]:
    """
    Rank and filter leak candidates.

    Args:
        candidates: List of leak candidates
        min_area: Minimum area threshold in m²
        top_k: Maximum number of candidates to return

    Returns:
        Filtered and ranked candidates
    """
    logger.debug(
        f"Ranking {len(candidates)} candidates, min_area: {min_area}m², top_k: {top_k}",
    )

    # Filter by minimum area
    filtered = [c for c in candidates if c.area_m2 >= min_area]

    # Sort by area descending
    ranked = sorted(filtered, key=lambda x: x.area_m2, reverse=True)

    # Return top k
    return ranked[:top_k]

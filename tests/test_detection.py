"""Test detection module."""

import numpy as np
import pytest

from aquaspot.detection import LeakCandidate, cluster_anomalies, rank_candidates


def test_leak_candidate_model():
    """Test LeakCandidate pydantic model."""
    candidate = LeakCandidate(
        geometry={
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
        },
        score=0.85,
        area_m2=150.0,
        centroid=(0.5, 0.5),
        bounding_box=(0.0, 0.0, 1.0, 1.0),
    )

    assert candidate.score == 0.85
    assert candidate.area_m2 == 150.0
    assert candidate.centroid == (0.5, 0.5)


def test_cluster_anomalies_not_implemented():
    """Test cluster_anomalies raises NotImplementedError."""
    masked_ndwi = np.random.random((10, 10))
    pixel_size_m = 10.0

    with pytest.raises(NotImplementedError):
        cluster_anomalies(masked_ndwi, pixel_size_m)


def test_rank_candidates_empty_list():
    """Test rank_candidates with empty list."""
    candidates = []
    result = rank_candidates(candidates)
    assert result == []


def test_rank_candidates_filtering():
    """Test rank_candidates filters by minimum area."""
    candidates = [
        LeakCandidate(
            geometry={},
            score=0.8,
            area_m2=30.0,
            centroid=(0, 0),
            bounding_box=(0, 0, 1, 1),
        ),
        LeakCandidate(
            geometry={},
            score=0.7,
            area_m2=20.0,  # Below min_area
            centroid=(0, 0),
            bounding_box=(0, 0, 1, 1),
        ),
        LeakCandidate(
            geometry={},
            score=0.9,
            area_m2=50.0,
            centroid=(0, 0),
            bounding_box=(0, 0, 1, 1),
        ),
    ]

    result = rank_candidates(candidates, min_area=25, top_k=10)

    # Should filter out candidate with area < 25
    assert len(result) == 2
    # Should be sorted by area descending
    assert result[0].area_m2 == 50.0
    assert result[1].area_m2 == 30.0


def test_rank_candidates_top_k():
    """Test rank_candidates respects top_k limit."""
    candidates = [
        LeakCandidate(
            geometry={},
            score=0.8,
            area_m2=float(i * 10),
            centroid=(0, 0),
            bounding_box=(0, 0, 1, 1),
        )
        for i in range(1, 6)  # 5 candidates with areas 10, 20, 30, 40, 50
    ]

    result = rank_candidates(candidates, min_area=0, top_k=3)

    assert len(result) == 3
    # Should return largest 3 areas: 50, 40, 30
    assert result[0].area_m2 == 50.0
    assert result[1].area_m2 == 40.0
    assert result[2].area_m2 == 30.0

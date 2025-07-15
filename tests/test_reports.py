"""Test reports module."""

from pathlib import Path

import pytest

from aquaspot.detection import LeakCandidate
from aquaspot.reports import build_pdf


def test_build_pdf_not_implemented():
    """Test build_pdf raises NotImplementedError."""
    candidates = [
        LeakCandidate(
            geometry={},
            score=0.8,
            area_m2=100.0,
            centroid=(0, 0),
            bounding_box=(0, 0, 1, 1),
        ),
    ]
    out_path = Path("test_report.pdf")

    with pytest.raises(NotImplementedError):
        build_pdf(candidates, out_path)

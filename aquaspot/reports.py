"""
Report generation and visualization.

Handles PDF report creation and map visualizations for
leak detection results.
"""

import logging
from pathlib import Path

from aquaspot.detection import LeakCandidate

logger = logging.getLogger(__name__)


def build_pdf(candidates: list[LeakCandidate], out_path: Path) -> None:
    """
    Generate PDF report from leak candidates.

    Args:
        candidates: List of leak candidates to include
        out_path: Output path for PDF file

    Raises:
        ValueError: If candidates list is empty
        IOError: If PDF generation fails
    """
    logger.debug(
        f"Building PDF report with {len(candidates)} candidates to: {out_path}",
    )

    # TODO: Implement WeasyPrint + Jinja2 template-based PDF generation
    # TODO: Include maps, thumbnails, and candidate details

    msg = "PDF generation not yet implemented"
    raise NotImplementedError(msg)

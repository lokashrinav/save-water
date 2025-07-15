"""Test alerts module."""

from pathlib import Path

import pytest

from aquaspot.alerts import send_email, send_sms
from aquaspot.detection import LeakCandidate


def test_send_email_not_implemented():
    """Test send_email raises NotImplementedError."""
    pdf_path = Path("test_report.pdf")
    recipients = ["test@example.com"]

    with pytest.raises(NotImplementedError):
        send_email(pdf_path, recipients)


def test_send_sms_not_implemented():
    """Test send_sms raises NotImplementedError."""
    candidate = LeakCandidate(
        geometry={},
        score=0.9,
        area_m2=100.0,
        centroid=(0, 0),
        bounding_box=(0, 0, 1, 1),
    )
    phone = "+1234567890"

    with pytest.raises(NotImplementedError):
        send_sms(candidate, phone)

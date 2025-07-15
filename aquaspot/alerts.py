"""
Alert and notification system.

Handles email and SMS notifications for detected pipeline leaks.
"""

import logging
from pathlib import Path

from aquaspot.detection import LeakCandidate

logger = logging.getLogger(__name__)


def send_email(pdf_path: Path, recipients: list[str]) -> None:
    """
    Send email alert with PDF report attachment.

    Args:
        pdf_path: Path to PDF report file
        recipients: List of email addresses

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ConnectionError: If SMTP server is unavailable
    """
    logger.debug(
        f"Sending email alert to {len(recipients)} recipients with PDF: {pdf_path}",
    )

    # TODO: Implement SMTP-based email sending
    # TODO: Include PDF attachment and formatted message

    msg = "Email alerts not yet implemented"
    raise NotImplementedError(msg)


def send_sms(candidate: LeakCandidate, to_phone: str) -> None:
    """
    Send SMS alert for high-priority leak candidate.

    Args:
        candidate: Leak candidate to alert about
        to_phone: Phone number to send SMS to

    Raises:
        ValueError: If phone number format is invalid
        ConnectionError: If Twilio API is unavailable
    """
    logger.debug(
        f"Sending SMS alert for candidate with score {candidate.score} to: {to_phone}",
    )

    # TODO: Implement Twilio-based SMS sending
    # TODO: Format message with candidate details

    msg = "SMS alerts not yet implemented"
    raise NotImplementedError(msg)

"""PDF generation for lifeboat familiarisation notices."""

from pathlib import Path


def generate_pdf(personnel: list[str], vessel_name: str = "") -> Path:
    """
    Generate PDF notice for lifeboat familiarisation.

    Args:
        personnel: List of personnel names to include
        vessel_name: Optional vessel name for the header

    Returns:
        Path to generated PDF file

    Raises:
        RuntimeError: If PDF generation fails
    """
    raise NotImplementedError("PDF generation not yet implemented")

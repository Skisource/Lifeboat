"""PDF generation for lifeboat familiarisation notices."""

import os
import tempfile
from datetime import datetime
from pathlib import Path

from flask import current_app, render_template
from weasyprint import HTML


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
    today = datetime.now().strftime("%d %B %Y")

    html_content = render_template(
        "pdf_template.html",
        personnel=personnel,
        vessel_name=vessel_name,
        date=today,
    )

    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    output_path = Path(temp_path)

    try:
        html = HTML(string=html_content, base_url=current_app.root_path)
        html.write_pdf(output_path)
    except Exception as e:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(f"Failed to generate PDF: {e}") from e

    return output_path

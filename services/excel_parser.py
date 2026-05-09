"""Excel file parsing for familiarisation and POB lists."""

import re
from typing import BinaryIO

import openpyxl


def normalize_name(name: str) -> str:
    """
    Normalize a name for comparison.

    Handles both "First Last" and "Last, First" formats.
    Returns lowercase "first last" format.
    """
    name = name.strip()

    if "," in name:
        parts = name.split(",", 1)
        if len(parts) == 2:
            last, first = parts
            name = f"{first.strip()} {last.strip()}"

    name = re.sub(r"\s+", " ", name)
    return name.lower()


def parse_familiarisation_list(file: BinaryIO) -> list[str]:
    """
    Parse familiarisation required list from xlsx file.

    Expected format:
    - Row 3: Headers (Site, Full Name, Occupation, First Expiry)
    - Row 4+: Data with names in column B (Full Name)

    Args:
        file: File-like object containing xlsx data

    Returns:
        List of personnel names requiring familiarisation

    Raises:
        ValueError: If file format is invalid or required columns missing
    """
    try:
        wb = openpyxl.load_workbook(file, read_only=True, data_only=True)
    except Exception as e:
        raise ValueError(f"Could not read familiarisation file: {e}") from e

    ws = wb.active
    if ws is None:
        raise ValueError("Familiarisation file has no active worksheet")

    names = []
    for row in ws.iter_rows(min_row=4, values_only=True):
        if len(row) < 2:
            continue

        name = row[1]
        if name and isinstance(name, str) and name.strip():
            names.append(name.strip())

    wb.close()

    if not names:
        raise ValueError("No names found in familiarisation file")

    return names


def parse_pob_list(file: BinaryIO) -> list[str]:
    """
    Parse Personnel On Board list from xlsx file.

    Expected format:
    - Row 2: Headers (Person Onboard, Cabin, Occupation, ...)
    - Row 3+: Data with names in column A, but includes category/department rows

    Args:
        file: File-like object containing xlsx data

    Returns:
        List of personnel names currently on board

    Raises:
        ValueError: If file format is invalid or required columns missing
    """
    try:
        wb = openpyxl.load_workbook(file, read_only=True, data_only=True)
    except Exception as e:
        raise ValueError(f"Could not read POB file: {e}") from e

    ws = wb.active
    if ws is None:
        raise ValueError("POB file has no active worksheet")

    names = []
    skip_patterns = [
        r"^Category:",
        r"^Department:",
        r"^Total POB:",
        r"^Person Onboard$",
    ]
    skip_regex = re.compile("|".join(skip_patterns), re.IGNORECASE)

    for row in ws.iter_rows(min_row=3, values_only=True):
        if not row or not row[0]:
            continue

        cell_value = row[0]
        if not isinstance(cell_value, str):
            continue

        cell_value = cell_value.strip()
        if not cell_value:
            continue

        if skip_regex.search(cell_value):
            continue

        if "," in cell_value:
            names.append(cell_value)

    wb.close()

    if not names:
        raise ValueError("No names found in POB file")

    return names


def cross_reference(fam_names: list[str], pob_names: list[str]) -> list[str]:
    """
    Find personnel who are both on familiarisation list and currently on board.

    Handles different name formats:
    - Familiarisation uses "First Last"
    - POB uses "Last, First"

    Args:
        fam_names: Names requiring familiarisation
        pob_names: Names currently on board (in "Last, First" format)

    Returns:
        List of matched personnel names in display format (sorted alphabetically)
    """
    fam_normalized = {normalize_name(name): name for name in fam_names}
    pob_normalized = {normalize_name(name): name for name in pob_names}

    matched_keys = set(fam_normalized.keys()) & set(pob_normalized.keys())

    matched = [pob_normalized[key] for key in matched_keys]
    return sorted(matched, key=lambda x: normalize_name(x))

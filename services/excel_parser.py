"""Excel file parsing for familiarisation and POB lists."""

from typing import BinaryIO


def parse_familiarisation_list(file: BinaryIO) -> list[str]:
    """
    Parse familiarisation required list from xlsx file.

    Args:
        file: File-like object containing xlsx data

    Returns:
        List of personnel names requiring familiarisation

    Raises:
        ValueError: If file format is invalid or required columns missing
    """
    raise NotImplementedError("Excel parsing not yet implemented")


def parse_pob_list(file: BinaryIO) -> list[str]:
    """
    Parse Personnel On Board list from xlsx file.

    Args:
        file: File-like object containing xlsx data

    Returns:
        List of personnel names currently on board

    Raises:
        ValueError: If file format is invalid or required columns missing
    """
    raise NotImplementedError("Excel parsing not yet implemented")


def cross_reference(fam_names: list[str], pob_names: list[str]) -> list[str]:
    """
    Find personnel who are both on familiarisation list and currently on board.

    Args:
        fam_names: Names requiring familiarisation
        pob_names: Names currently on board

    Returns:
        List of matched personnel names (sorted alphabetically)
    """
    fam_normalized = {name.strip().lower(): name for name in fam_names}
    pob_normalized = {name.strip().lower(): name for name in pob_names}

    matched_keys = set(fam_normalized.keys()) & set(pob_normalized.keys())

    matched = [pob_normalized[key] for key in matched_keys]
    return sorted(matched, key=str.lower)

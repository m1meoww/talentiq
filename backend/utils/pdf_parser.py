"""
Robust PDF text extraction: PyMuPDF (fitz) primary, pypdf fallback.
Detects scanned/image-only, empty, and invalid PDFs and raises a clear,
user-facing PDFParseError instead of crashing.
"""


class PDFParseError(Exception):
    def __init__(self, message: str, code: str = "invalid_pdf"):
        super().__init__(message)
        self.code = code


def _extract_with_fitz(file_path: str) -> str:
    import fitz  # PyMuPDF
    text_chunks = []
    with fitz.open(file_path) as doc:
        for page in doc:
            text_chunks.append(page.get_text())
    return "\n".join(text_chunks)


def _extract_with_pypdf(file_path: str) -> str:
    from pypdf import PdfReader
    reader = PdfReader(file_path)
    text_chunks = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(text_chunks)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Returns extracted plain text. Raises PDFParseError with a descriptive,
    user-facing message for invalid, empty, or scanned/image-only PDFs.
    """
    text = ""
    errors = []

    try:
        text = _extract_with_fitz(file_path)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"PyMuPDF: {exc}")

    if not text or not text.strip():
        try:
            text = _extract_with_pypdf(file_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"pypdf: {exc}")

    if errors and not text.strip():
        raise PDFParseError(
            "This file could not be opened as a valid PDF. Please re-export "
            "and re-upload the resume.",
            code="corrupt_pdf",
        )

    if not text or not text.strip():
        raise PDFParseError(
            "No extractable text was found in this PDF. It looks like a "
            "scanned or image-only document — please upload a text-based "
            "PDF resume instead.",
            code="scanned_pdf",
        )

    return text.strip()

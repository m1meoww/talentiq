import os
import uuid
from werkzeug.utils import secure_filename

from models import db, CandidateProfile
from utils.pdf_parser import extract_text_from_pdf, PDFParseError
from ml.pipeline import analyze_resume


def save_uploaded_resume(file_storage, upload_folder: str) -> str:
    os.makedirs(upload_folder, exist_ok=True)
    original_name = secure_filename(file_storage.filename or "resume.pdf")
    unique_name = f"{uuid.uuid4().hex}_{original_name}"
    dest_path = os.path.join(upload_folder, unique_name)
    file_storage.save(dest_path)
    return dest_path


def process_resume_upload(candidate: CandidateProfile, file_storage, upload_folder: str,
                           position=None):
    """
    Saves the file, extracts text, runs the ML pipeline, and updates the
    candidate profile. Returns the analysis dict. Raises PDFParseError on
    invalid/scanned/empty PDFs -- callers should surface .args[0] to the user.
    """
    dest_path = save_uploaded_resume(file_storage, upload_folder)

    try:
        text = extract_text_from_pdf(dest_path)
    except PDFParseError:
        raise

    analysis = analyze_resume(text, position=position)

    candidate.resume_path = dest_path
    candidate.extracted_resume_text = text
    candidate.predicted_category = analysis.get("predicted_category")
    db.session.add(candidate)
    db.session.commit()

    return analysis

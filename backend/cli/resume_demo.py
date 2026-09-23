"""
TalentIQ CLI Demonstration Tool.

Usage:
    python cli/resume_demo.py --email candidate@talentiq.ai --resume /path/to/resume.pdf

Extracts resume text, runs the full ML pipeline, and prints the predicted
category, overall match %, and ranking against all open positions as clean
ANSI-formatted tables.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"


def color_for_score(score):
    if score >= 70:
        return GREEN
    if score >= 45:
        return YELLOW
    return RED


def print_table(headers, rows):
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    def fmt_row(row):
        return " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(row))

    print(f"{BOLD}{fmt_row(headers)}{RESET}")
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(fmt_row(row))


def main():
    parser = argparse.ArgumentParser(description="TalentIQ resume screening CLI demo.")
    parser.add_argument("--email", required=True, help="Candidate email to identify/create the profile.")
    parser.add_argument("--resume", required=True, help="Path to a PDF resume file.")
    args = parser.parse_args()

    if not os.path.exists(args.resume):
        print(f"{RED}Error: resume file not found at {args.resume}{RESET}")
        sys.exit(1)

    from app import create_app
    from models import db, User, CandidateProfile, JobPosition
    from utils.pdf_parser import extract_text_from_pdf, PDFParseError
    from ml.pipeline import analyze_resume, rank_candidates_for_position

    app = create_app()
    with app.app_context():
        print(f"{CYAN}{BOLD}TalentIQ — AI-Powered Recruitment Intelligence (CLI Demo){RESET}")
        print(f"Candidate: {args.email}\nResume:    {args.resume}\n")

        try:
            print("Step 1/6  Extracting text from PDF...")
            text = extract_text_from_pdf(args.resume)
        except PDFParseError as exc:
            print(f"{RED}{exc}{RESET}")
            sys.exit(1)

        print("Step 2/6  Cleaning & preprocessing text...")
        print("Step 3/6  Building TF-IDF representation...")
        print("Step 4/6  Reducing dimensions with SVD...")
        print("Step 5/6  Calculating cosine similarity against positions...")
        print("Step 6/6  Generating scores & category prediction...\n")

        category = analyze_resume(text)
        print(f"{BOLD}Predicted Category:{RESET} {category['predicted_category']} "
              f"({category['category_confidence']}% confidence, {category['category_mode']} mode)\n")

        positions = JobPosition.query.filter_by(status="Open").all()
        if not positions:
            print(f"{YELLOW}No open positions found in the database. Run the seeder first:{RESET}")
            print("  python -m database.seed")
            return

        rows = []
        for pos in positions:
            from ml.similarity import score_resume_against_text
            result = score_resume_against_text(
                resume_text=text, position_text=pos.full_text(),
                required_skills=(pos.preferred_skills or "").split(","),
            )
            rows.append((pos.title, pos.department, f"{result['overall_match']}%"))

        rows.sort(key=lambda r: float(r[2].strip("%")), reverse=True)
        print(f"{BOLD}Ranking against all open positions:{RESET}")
        print_table(["Position", "Department", "Match %"], rows)


if __name__ == "__main__":
    main()

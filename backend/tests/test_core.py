"""
Core automated tests: ML scoring, auth, candidates/positions/applications CRUD,
audit history, and chatbot intent resolution.

Run with: python -m unittest discover tests   (from backend/)
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DB_ENGINE"] = "sqlite"


class TalentIQTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use an isolated in-memory-ish SQLite file for tests.
        cls.tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        os.environ["MYSQL_HOST"] = ""  # force sqlite path
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def setUp(self):
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    # ---- ML ----
    def test_similarity_scoring_is_bounded(self):
        from ml.similarity import score_resume_against_text
        result = score_resume_against_text(
            "5 years python django machine learning tensorflow",
            "Looking for a python developer with 3+ years machine learning experience",
            required_skills=["python", "machine learning", "django"],
        )
        self.assertGreaterEqual(result["overall_match"], 0)
        self.assertLessEqual(result["overall_match"], 100)
        self.assertIn("python", result["matched_skills"] + result["missing_skills"])

    def test_similarity_handles_empty_text_gracefully(self):
        from ml.similarity import score_resume_against_text
        result = score_resume_against_text("", "", [])
        self.assertEqual(result["overall_match"], round(result["overall_match"], 1))

    def test_classifier_returns_known_category(self):
        from ml.classifier import predict_category, CATEGORIES
        result = predict_category("Experienced with pytorch tensorflow deep learning neural networks")
        self.assertIn(result["category"], CATEGORIES)

    # ---- PDF parsing ----
    def test_pdf_parser_rejects_invalid_file(self):
        from utils.pdf_parser import extract_text_from_pdf, PDFParseError
        bad_path = os.path.join(tempfile.gettempdir(), "not_a_real.pdf")
        with open(bad_path, "wb") as f:
            f.write(b"this is not a pdf")
        with self.assertRaises(PDFParseError):
            extract_text_from_pdf(bad_path)

    # ---- Auth ----
    def test_register_and_login(self):
        resp = self.client.post("/api/auth/register", json={
            "name": "Test User", "email": "test.user@example.com",
            "password": "Passw0rd!", "role": "Candidate",
        })
        self.assertEqual(resp.status_code, 201)

        resp = self.client.post("/api/auth/login", json={
            "email": "test.user@example.com", "password": "Passw0rd!",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn("token", resp.get_json())

    def test_login_rejects_bad_password(self):
        self.client.post("/api/auth/register", json={
            "name": "Test User 2", "email": "test2@example.com",
            "password": "Passw0rd!", "role": "Candidate",
        })
        resp = self.client.post("/api/auth/login", json={
            "email": "test2@example.com", "password": "wrong",
        })
        self.assertEqual(resp.status_code, 401)

    # ---- Positions & Applications ----
    def test_position_crud_and_application_flow(self):
        reg = self.client.post("/api/auth/register", json={
            "name": "HR One", "email": "hr1@example.com",
            "password": "Passw0rd!", "role": "HR",
        }).get_json()
        token = reg["token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = self.client.post("/api/positions", json={
            "title": "Test Engineer", "department": "Engineering",
            "requirements": "3+ years python",
            "preferred_skills": ["python", "sql"],
        }, headers=headers)
        self.assertEqual(resp.status_code, 201)
        position_id = resp.get_json()["id"]

        cand_reg = self.client.post("/api/auth/register", json={
            "name": "Cand One", "email": "cand1@example.com",
            "password": "Passw0rd!", "role": "Candidate",
        }).get_json()
        from models import CandidateProfile, User
        cand_user = User.query.filter_by(email="cand1@example.com").first()
        candidate = CandidateProfile.query.filter_by(user_id=cand_user.id).first()
        candidate.extracted_resume_text = "5 years python sql experience"
        from models import db
        db.session.commit()

        resp = self.client.post("/api/applications", json={
            "candidate_id": candidate.id, "position_id": position_id,
        }, headers=headers)
        self.assertEqual(resp.status_code, 201)
        application_id = resp.get_json()["id"]

        resp = self.client.put(f"/api/applications/{application_id}/status",
                                json={"status": "Shortlisted", "remarks": "Great fit"},
                                headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["status"], "Shortlisted")

        resp = self.client.get(f"/api/applications/{application_id}/history", headers=headers)
        history = resp.get_json()["history"]
        self.assertGreaterEqual(len(history), 2)

    # ---- Chatbot ----
    def test_chatbot_fallback_reply(self):
        from services.chatbot_service import get_reply
        result = get_reply("asdkjaslkdj random gibberish")
        self.assertEqual(result["intent"], "fallback")


if __name__ == "__main__":
    unittest.main()

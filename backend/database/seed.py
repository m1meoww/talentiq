"""
Synthetic data seeder for TalentIQ.

Generates:
  - 3 default accounts (Admin / HR Recruiter / Candidate)
  - 10 job positions across engineering, AI/ML, data science, cybersecurity, product
  - 25 synthetic candidates with rich profiles + skills
  - 40 applications across the full lifecycle with audit history
  - Programmatically generated sample PDF resumes in sample_data/resumes/

Run standalone with `python -m database.seed` (from backend/) or is invoked
automatically by app.py on first boot against an empty database.
"""
import os
import random
import datetime as dt

from models import db, User, CandidateProfile, JobPosition, Application, ApplicationHistory
from models.application import STATUSES

random.seed(7)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
SAMPLE_RESUME_DIR = os.path.join(os.path.dirname(BASE_DIR), "database", "sample_data", "resumes")

FIRST_NAMES = [
    "Aarav", "Ananya", "Rohan", "Ishita", "Arjun", "Neha", "Kabir", "Meera",
    "Vivaan", "Diya", "Aditya", "Sanya", "Karthik", "Priya", "Nikhil", "Tara",
    "Rahul", "Simran", "Aryan", "Pooja", "Dhruv", "Kavya", "Yash", "Riya", "Siddharth",
]
LAST_NAMES = [
    "Sharma", "Mehta", "Kapoor", "Verma", "Malhotra", "Singh", "Khanna", "Joshi",
    "Reddy", "Nair", "Iyer", "Gupta", "Chatterjee", "Bhatt", "Rao", "Menon",
    "Chawla", "Desai", "Kulkarni", "Agarwal", "Bose", "Pillai", "Trivedi", "Saxena", "Bansal",
]

CITIES = ["Bengaluru", "Hyderabad", "Pune", "Gurugram", "Mumbai", "Chennai", "Noida", "Kolkata"]

POSITIONS = [
    dict(title="Software Engineer II", department="Engineering",
         requirements="3+ years experience with Python, Java, REST APIs and microservices.",
         preferred_skills="python,java,rest api,microservices,git,sql",
         experience_level="Mid"),
    dict(title="Senior Backend Engineer", department="Engineering",
         requirements="5+ years backend experience, distributed systems, Node.js or Java.",
         preferred_skills="node.js,java,distributed systems,kafka,docker,kubernetes",
         experience_level="Senior"),
    dict(title="Frontend Engineer", department="Engineering",
         requirements="3+ years with React, TypeScript, responsive design.",
         preferred_skills="react,typescript,javascript,css,html,redux",
         experience_level="Mid"),
    dict(title="Data Scientist", department="Data Science",
         requirements="3+ years experience with Python, pandas, statistics, regression modeling.",
         preferred_skills="python,pandas,numpy,statistics,sql,regression,visualization",
         experience_level="Mid"),
    dict(title="AI/ML Engineer", department="AI/ML",
         requirements="4+ years in machine learning, deep learning, PyTorch or TensorFlow, NLP.",
         preferred_skills="machine learning,deep learning,pytorch,tensorflow,nlp,scikit-learn",
         experience_level="Senior"),
    dict(title="Machine Learning Researcher", department="AI/ML",
         requirements="PhD or 5+ years research experience in deep learning and computer vision.",
         preferred_skills="deep learning,computer vision,pytorch,research,neural network",
         experience_level="Senior"),
    dict(title="Cybersecurity Analyst", department="Cybersecurity",
         requirements="3+ years in SOC operations, SIEM tools, vulnerability management.",
         preferred_skills="siem,vulnerability,incident response,firewall,soc",
         experience_level="Mid"),
    dict(title="Cloud/DevOps Engineer", department="Cloud/DevOps",
         requirements="4+ years with AWS, Kubernetes, Terraform, CI/CD pipelines.",
         preferred_skills="aws,kubernetes,terraform,ci/cd,docker,jenkins",
         experience_level="Senior"),
    dict(title="Product Manager", department="Product",
         requirements="4+ years product management, roadmap ownership, stakeholder management.",
         preferred_skills="product strategy,roadmap,stakeholder,agile,user research",
         experience_level="Senior"),
    dict(title="Recruitment Operations Specialist", department="Operations",
         requirements="2+ years in operations, process improvement, vendor management.",
         preferred_skills="operations,process improvement,vendor management,sop",
         experience_level="Junior"),
]

RESUME_TEMPLATE = """{name}
{email} | {phone} | {location}

SUMMARY
{summary}

EXPERIENCE
{years} years of professional experience in {domain}. Worked on projects involving
{skills_line}. Delivered measurable impact across cross-functional teams.

EDUCATION
{education}

SKILLS
{skills_line}
"""


def _make_pdf_resume(path, name, email, phone, location, summary, years, domain, skills_line, education):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    text = c.beginText(40, height - 60)
    text.setFont("Helvetica-Bold", 14)
    text.textLine(name)
    text.setFont("Helvetica", 10)
    text.textLine(f"{email} | {phone} | {location}")
    text.textLine("")
    text.setFont("Helvetica-Bold", 11)
    text.textLine("SUMMARY")
    text.setFont("Helvetica", 10)
    for line in _wrap(summary, 95):
        text.textLine(line)
    text.textLine("")
    text.setFont("Helvetica-Bold", 11)
    text.textLine("EXPERIENCE")
    text.setFont("Helvetica", 10)
    exp_text = (f"{years} years of professional experience in {domain}. Worked on projects "
                f"involving {skills_line}. Delivered measurable impact across teams.")
    for line in _wrap(exp_text, 95):
        text.textLine(line)
    text.textLine("")
    text.setFont("Helvetica-Bold", 11)
    text.textLine("EDUCATION")
    text.setFont("Helvetica", 10)
    text.textLine(education)
    text.textLine("")
    text.setFont("Helvetica-Bold", 11)
    text.textLine("SKILLS")
    text.setFont("Helvetica", 10)
    for line in _wrap(skills_line, 95):
        text.textLine(line)
    c.drawText(text)
    c.showPage()
    c.save()


def _wrap(text, width):
    words = text.split()
    lines, current = [], ""
    for w in words:
        if len(current) + len(w) + 1 <= width:
            current = f"{current} {w}".strip()
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


DOMAINS = {
    "Software Engineering": "backend and API development",
    "Data Science": "data analysis and statistical modeling",
    "AI/ML": "machine learning and deep learning systems",
    "Cybersecurity": "security operations and threat detection",
    "Cloud/DevOps": "cloud infrastructure and automation",
    "Product": "product strategy and roadmap execution",
    "Operations": "recruitment and process operations",
}

EDUCATION_OPTIONS = [
    "B.Tech in Computer Science, IIT Delhi (2018)",
    "M.Tech in Data Science, IIIT Hyderabad (2020)",
    "B.Sc in Computer Applications, Pune University (2017)",
    "MBA in Operations, ISB Hyderabad (2021)",
    "B.E in Information Technology, Anna University (2016)",
    "M.Sc in Artificial Intelligence, IISc Bengaluru (2021)",
]


def run_seed():
    os.makedirs(SAMPLE_RESUME_DIR, exist_ok=True)

    # ---- Default accounts ----
    admin = User(name="TalentIQ Admin", email="admin@talentiq.ai", role="Admin")
    admin.set_password("Admin@123")
    recruiter = User(name="Priya Recruiter", email="recruiter@talentiq.ai", role="HR")
    recruiter.set_password("Recruiter@123")
    demo_candidate_user = User(name="Demo Candidate", email="candidate@talentiq.ai", role="Candidate")
    demo_candidate_user.set_password("Candidate@123")
    db.session.add_all([admin, recruiter, demo_candidate_user])
    db.session.flush()
    db.session.add(CandidateProfile(
        user_id=demo_candidate_user.id, phone="+91 90000 00000", location="Bengaluru",
        experience_years=3, skills="python,react,sql", summary="Demo evaluation account.",
    ))

    # ---- Positions ----
    positions = []
    for p in POSITIONS:
        pos = JobPosition(
            title=p["title"], department=p["department"],
            description=f"We are hiring a {p['title']} to join the {p['department']} team.",
            requirements=p["requirements"], preferred_skills=p["preferred_skills"],
            location=random.choice(CITIES), employment_type="Full-time",
            experience_level=p["experience_level"], status="Open",
        )
        positions.append(pos)
    db.session.add_all(positions)
    db.session.flush()

    # ---- Candidates ----
    from ml.pipeline import analyze_resume

    candidates = []
    for i in range(25):
        first, last = FIRST_NAMES[i], LAST_NAMES[i]
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}@example.com"
        location = random.choice(CITIES)
        years = round(random.uniform(1, 9), 1)
        target_pos = random.choice(positions)
        domain = DOMAINS.get(target_pos.department, "technology")
        skills_line = target_pos.preferred_skills.replace(",", ", ")
        education = random.choice(EDUCATION_OPTIONS)
        summary = (f"{domain.capitalize()} professional with {years} years of experience "
                   f"building impactful, scalable solutions.")

        user = User(name=name, email=email, role="Candidate")
        user.set_password("Candidate@123")
        db.session.add(user)
        db.session.flush()

        resume_filename = f"{first.lower()}_{last.lower()}_resume.pdf"
        resume_path = os.path.join(SAMPLE_RESUME_DIR, resume_filename)
        try:
            _make_pdf_resume(resume_path, name, email, "+91 9" + str(random.randint(100000000, 999999999)),
                              location, summary, years, domain, skills_line, education)
        except Exception:  # noqa: BLE001
            resume_path = None

        resume_text = RESUME_TEMPLATE.format(
            name=name, email=email, phone="+91 9XXXXXXXXX", location=location,
            summary=summary, years=years, domain=domain, skills_line=skills_line,
            education=education,
        )

        category_info = analyze_resume(resume_text)

        profile = CandidateProfile(
            user_id=user.id, phone="+91 9" + str(random.randint(100000000, 999999999)),
            location=location, education=education, experience_years=years,
            skills=skills_line, resume_path=resume_path, extracted_resume_text=resume_text,
            summary=summary, predicted_category=category_info["predicted_category"],
        )
        db.session.add(profile)
        candidates.append(profile)

    db.session.flush()

    # ---- Applications (40 across lifecycle) ----
    from ml.similarity import score_resume_against_text

    pairs = set()
    applications_created = 0
    attempts = 0
    while applications_created < 40 and attempts < 400:
        attempts += 1
        cand = random.choice(candidates)
        pos = random.choice(positions)
        if (cand.id, pos.id) in pairs:
            continue
        pairs.add((cand.id, pos.id))

        scoring = score_resume_against_text(
            resume_text=cand.extracted_resume_text or "",
            position_text=pos.full_text(),
            required_skills=(pos.preferred_skills or "").split(","),
            resume_experience_years=cand.experience_years,
        )
        status = random.choices(
            STATUSES, weights=[25, 25, 20, 15, 8, 7], k=1
        )[0]
        applied_at = dt.datetime.utcnow() - dt.timedelta(days=random.randint(1, 60))

        application = Application(
            candidate_id=cand.id, position_id=pos.id,
            match_score=scoring["overall_match"], skill_score=scoring["skill_score"],
            experience_score=scoring["experience_score"], education_score=scoring["education_score"],
            keyword_score=scoring["keyword_score"],
            matched_skills=",".join(scoring["matched_skills"]),
            missing_skills=",".join(scoring["missing_skills"]),
            status=status, applied_at=applied_at,
        )
        db.session.add(application)
        db.session.flush()

        # Build a plausible audit trail leading up to the final status
        lifecycle = STATUSES[: STATUSES.index(status) + 1] if status != "Rejected" else ["Applied", "Under Review", "Rejected"]
        prev = None
        step_time = applied_at
        for step_status in lifecycle:
            db.session.add(ApplicationHistory(
                application_id=application.id, old_status=prev, new_status=step_status,
                changed_by="Priya Recruiter" if prev else cand.user.name,
                changed_at=step_time,
                remarks="Status updated." if prev else "Application submitted.",
            ))
            prev = step_status
            step_time += dt.timedelta(days=random.randint(1, 5))

        applications_created += 1

    db.session.commit()
    print(f"[TalentIQ] Seeded: 3 default users, {len(positions)} positions, "
          f"{len(candidates)} candidates, {applications_created} applications.")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
    from app import create_app
    app = create_app()
    with app.app_context():
        if User.query.first() is None:
            run_seed()
        else:
            print("[TalentIQ] Database already has data; skipping seed. "
                  "Delete talentiq.db to reseed from scratch.")

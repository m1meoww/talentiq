-- TalentIQ reference MySQL schema.
-- Note: in local development, SQLAlchemy's db.create_all() (see backend/app.py)
-- generates the equivalent schema automatically against SQLite or MySQL.
-- This file is provided for production MySQL deployments / manual review.

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'Candidate',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email)
);

CREATE TABLE IF NOT EXISTS candidate_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    phone VARCHAR(30),
    location VARCHAR(120),
    education TEXT,
    experience_years FLOAT DEFAULT 0,
    skills TEXT,
    resume_path VARCHAR(255),
    extracted_resume_text LONGTEXT,
    summary TEXT,
    predicted_category VARCHAR(80),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS job_positions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(160) NOT NULL,
    department VARCHAR(80),
    description TEXT,
    requirements TEXT,
    preferred_skills TEXT,
    location VARCHAR(120),
    employment_type VARCHAR(40) DEFAULT 'Full-time',
    experience_level VARCHAR(40) DEFAULT 'Mid',
    status VARCHAR(20) DEFAULT 'Open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    position_id INT NOT NULL,
    match_score FLOAT DEFAULT 0,
    skill_score FLOAT DEFAULT 0,
    experience_score FLOAT DEFAULT 0,
    education_score FLOAT DEFAULT 0,
    keyword_score FLOAT DEFAULT 0,
    matched_skills TEXT,
    missing_skills TEXT,
    status VARCHAR(20) DEFAULT 'Applied',
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_candidate_position (candidate_id, position_id),
    FOREIGN KEY (candidate_id) REFERENCES candidate_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (position_id) REFERENCES job_positions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS application_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_by VARCHAR(120),
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);

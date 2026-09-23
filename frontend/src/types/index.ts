export type Role = "Admin" | "HR" | "Candidate";

export interface AppUser {
  id: number;
  name: string;
  email: string;
  role: Role;
  created_at?: string;
}

export interface Candidate {
  id: number;
  user_id: number;
  name?: string;
  email?: string;
  phone?: string;
  location?: string;
  education?: string;
  experience_years?: number;
  skills: string[];
  resume_path?: string;
  summary?: string;
  predicted_category?: string;
  applications?: Application[];
}

export interface Position {
  id: number;
  title: string;
  department?: string;
  description?: string;
  requirements?: string;
  preferred_skills: string[];
  location?: string;
  employment_type?: string;
  experience_level?: string;
  status: string;
  created_at?: string;
  applicant_count?: number;
  avg_score?: number;
  rankings?: RankingRow[];
}

export interface RankingRow {
  candidate_id: number;
  candidate_name?: string;
  candidate_email?: string;
  predicted_category?: string;
  overall_match: number;
  semantic_similarity: number;
  skill_score: number;
  experience_score: number;
  education_score: number;
  keyword_score: number;
  matched_skills: string[];
  missing_skills: string[];
}

export interface ApplicationHistoryEntry {
  id: number;
  application_id: number;
  old_status: string | null;
  new_status: string;
  changed_by: string;
  changed_at: string;
  remarks?: string;
}

export interface Application {
  id: number;
  candidate_id: number;
  position_id: number;
  match_score: number;
  breakdown: {
    skill: number;
    experience: number;
    education: number;
    keyword: number;
  };
  matched_skills: string[];
  missing_skills: string[];
  status: string;
  applied_at?: string;
  updated_at?: string;
  candidate_name?: string;
  candidate_email?: string;
  position_title?: string;
  department?: string;
}

export interface KPIs {
  total_applicants: number;
  resumes_screened: number;
  open_positions: number;
  shortlisted: number;
  avg_match_score: number;
}

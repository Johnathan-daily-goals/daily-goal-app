export interface User {
  id: number;
  email: string;
}

// login/register returns a flat object with user fields + tokens at the top level
export interface AuthResponse {
  id: number;
  email: string;
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  archived_at: string | null;
}

export interface DailyGoal {
  id: number;
  project_id: number;
  goal_text: string;
  created_at: string;
}

export interface ApiError {
  error: string;
}

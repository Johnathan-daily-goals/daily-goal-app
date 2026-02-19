// These types mirror what the backend returns as JSON.
// Keeping them in one place means if the API changes,
// you update here and TypeScript will tell you everywhere else that breaks.

export interface User {
  id: number;
  email: string;
}

// The backend returns a flat object on login/register —
// user fields (id, email) are at the top level alongside the tokens.
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

// Shape of error responses from the backend: { "error": "some message" }
export interface ApiError {
  error: string;
}

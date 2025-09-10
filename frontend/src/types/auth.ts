export interface User {
  id: number;
  email: string;
  role: "user" | "admin"; // extend if needed
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
}

import api from "@/lib/api";
import { LoginResponse, User } from "@/types/auth";

export async function login(username: string, password: string): Promise<void> {
  const res = await api.post<LoginResponse>("/users/login", {
    username,
    password,
  });
  localStorage.setItem("access_token", res.data.access_token);
  localStorage.setItem("refresh_token", res.data.refresh_token);
  window.location.href = "/login";
}

export async function logout() {
  await api.post("/users/logout", {
    refresh_token: localStorage.getItem("access_token"),
  });
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/login";
}

export async function getCurrentUser(): Promise<User> {
  const res = await api.get<User>("/users/me");
  return res.data;
}

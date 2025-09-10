"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "../../services/auth";
import { useAuth } from "../../context/AuthContext";

export default function LoginPage() {
  const router = useRouter();
  const { user, loading } = useAuth(); // 🧠 get auth status
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  // 🛡️ redirect if already logged in
  useEffect(() => {
    if (!loading && user) {
      router.replace("./inventory/create");
    }
  }, [loading, user, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await login(username, password);
      router.replace("./inventory/create");
    } catch (err) {
      console.error(err);
      setError("Invalid username or password");
    }
  }

  // Optional: skip render if already authenticated
  if (!loading && user) return null;

  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm space-y-4 rounded border p-6 shadow"
      >
        <h1 className="text-center text-2xl font-bold">Login</h1>

        {error && <p className="text-center text-sm text-red-500">{error}</p>}

        <div>
          <label className="block text-sm font-medium">Username</label>
          <input
            type="text"
            value={username}
            required
            onChange={e => setUsername(e.target.value)}
            className="w-full rounded border px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium">Password</label>
          <input
            type="password"
            value={password}
            required
            onChange={e => setPassword(e.target.value)}
            className="w-full rounded border px-3 py-2"
          />
        </div>

        <button
          type="submit"
          className="w-full rounded bg-blue-600 py-2 font-semibold text-white hover:bg-blue-700"
        >
          Login
        </button>
      </form>
    </main>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Navigation from "@/components/ui/navigation";
import { useRouter } from "next/navigation";

interface LoginResponse {
  access_token?: string;
  user_email?: string;
  detail?: string;
}

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  // ✅ Capture token & user_email from query params
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    const user_email = params.get("user_email");

    if (token) localStorage.setItem("token", token);
    if (user_email) localStorage.setItem("user_email", user_email);

    if (token || user_email) {
      // Clean URL
      window.history.replaceState({}, document.title, "/login");
      router.replace("/dashboard");
    }
  }, [router]);

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const res = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      const data: LoginResponse = await res.json();

      if (!res.ok) throw new Error(data.detail ?? "Invalid credentials");

      // ✅ Store token & user_email for email login as well
      if (data.access_token) localStorage.setItem("token", data.access_token);
      if (data.user_email)
        localStorage.setItem("user_email", data.user_email ?? email);

      router.replace("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex flex-col items-center">
      <Navigation />
      <div className="max-w-md w-full mt-16 bg-white shadow-lg rounded-2xl p-8 space-y-6">
        <h2 className="text-center text-2xl font-bold text-gray-800">
          Sign in
        </h2>

        <form onSubmit={handleEmailLogin} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 text-black"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 text-black"
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <button
          type="button"
          onClick={() => {
            window.location.href = "http://localhost:8000/auth/google/login";
          }}
          className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 flex items-center justify-center"
        >
          Continue with Google
        </button>

        {error && (
          <div className="text-red-500 text-sm text-center">{error}</div>
        )}

        <p className="text-sm text-center text-gray-600">
          Don’t have an account?{" "}
          <Link href="/signup" className="text-blue-600 hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </main>
  );
}

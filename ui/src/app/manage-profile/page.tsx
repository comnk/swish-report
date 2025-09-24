"use client";

import { useState, useEffect } from "react";
import Navigation from "@/components/navigation";

export default function ManageProfile() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch current user info using token only
  useEffect(() => {
    const fetchUserInfo = async () => {
      const token = localStorage.getItem("token");

      if (!token) {
        setError("You must be signed in to manage your profile.");
        return;
      }

      // Decode JWT to check expiration
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        const exp = payload.exp * 1000; // convert to ms
        if (Date.now() > exp) {
          setError("Session expired. Please log in again.");
          localStorage.clear();
          window.location.href = "/login";
          return;
        }
      } catch (err) {
        console.error("Invalid token:", err);
        setError("Invalid session. Please log in again.");
        localStorage.clear();
        window.location.href = "/login";
        return;
      }

      try {
        const res = await fetch("http://localhost:8000/user/user-info", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.detail || "Failed to fetch user info");
        }

        const data = await res.json();
        setUsername(data.username || "");
        setEmail(data.email || "");
      } catch (err) {
        console.error("Error fetching user info:", err);
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    };

    fetchUserInfo();
  }, []);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const token = localStorage.getItem("token");
    if (!token) {
      setError("You must be signed in to update your profile.");
      setLoading(false);
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/auth/update-profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ username, email, password }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Update failed");
      }

      alert("Profile updated successfully! Redirecting to dashboard...");
      setPassword("");
      window.location.href = "/dashboard";
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (
      !confirm(
        "Are you sure you want to delete your account? This action cannot be undone."
      )
    )
      return;

    const token = localStorage.getItem("token");
    if (!token) {
      setError("You must be signed in to delete your account.");
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/auth/delete-profile", {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Delete failed");
      }

      alert("Account deleted!");
      localStorage.clear();
      window.location.href = "/";
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Something went wrong.");
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <Navigation />
      <div className="max-w-md mx-auto mt-10 bg-white rounded-2xl shadow-md p-6 text-black">
        <h1 className="text-2xl font-bold mb-6">Manage Profile</h1>

        {error && <p className="text-red-600 mb-4">{error}</p>}

        <form onSubmit={handleUpdate} className="space-y-4">
          {/* Username */}
          <div>
            <label className="block text-sm font-medium mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          {/* New Password */}
          <div>
            <label className="block text-sm font-medium mb-1">
              New Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Leave blank to keep current password"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
          >
            {loading ? "Updating..." : "Update Profile"}
          </button>
        </form>

        <hr className="my-6" />

        {/* Delete Account */}
        <button
          onClick={handleDelete}
          className="w-full bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition-colors"
        >
          Delete Account
        </button>
      </div>
    </main>
  );
}

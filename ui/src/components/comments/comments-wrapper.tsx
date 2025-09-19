"use client";
import { useEffect, useState } from "react";
import CommentsSection from "./threaded-comments";

interface Props {
  parentId: number;
  contextType: "hs-scouting" | "college-scouting" | "nba-scouting";
}

export default function CommentsWrapper({ parentId, contextType }: Props) {
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const email = localStorage.getItem("user_email");
    if (!token || !email) return;

    const fetchUsername = async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/user/get-username/${email}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (!res.ok) throw new Error("Failed to fetch username");
        const data = await res.json();
        setUsername(data.username);
      } catch (err) {
        console.error(err);
      }
    };

    fetchUsername();
  }, []);

  if (!username)
    return (
      <p className="text-gray-500 mt-4">
        Sign in to participate in the discussion.
      </p>
    );

  return (
    <CommentsSection
      parentId={parentId}
      contextType={contextType}
      username={username}
    />
  );
}

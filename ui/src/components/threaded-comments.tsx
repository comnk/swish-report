"use client";

import { useEffect, useState } from "react";

type CommentType = {
  comment_id: number;
  parent_id: number;
  username: string;
  content: string;
  parent_comment_id?: number | null;
  created_at: string;
  replies: CommentType[];
};

interface CommentsSectionProps {
  parentId: number;
  contextType:
    | "hot-take"
    | "lineup"
    | "hs-scouting"
    | "college-scouting"
    | "nba-scouting";
  username: string;
}

function CommentItem({
  comment,
  onReply,
}: {
  comment: CommentType;
  onReply: (parentId: number | null, content: string) => void;
}) {
  const [replyText, setReplyText] = useState("");
  const [showReply, setShowReply] = useState(false);

  const handleReply = () => {
    if (replyText.trim()) {
      onReply(comment.comment_id, replyText);
      setReplyText("");
      setShowReply(false);
    }
  };

  return (
    <div className="border-l pl-4 mt-2 text-black">
      <p className="font-medium text-black">
        {comment.username}{" "}
        <span className="text-gray-500 text-sm">
          {new Date(comment.created_at).toLocaleString()}
        </span>
      </p>
      <p>{comment.content}</p>
      <button
        onClick={() => setShowReply(!showReply)}
        className="text-blue-600 text-sm mt-1"
      >
        Reply
      </button>

      {showReply && (
        <div className="flex gap-2 mt-1">
          <input
            type="text"
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            placeholder="Write a reply..."
            className="flex-1 border rounded px-2 py-1 text-black"
          />
          <button
            onClick={handleReply}
            className="bg-blue-600 text-white px-3 py-1 rounded"
          >
            Post
          </button>
        </div>
      )}

      {comment.replies.map((reply) => (
        <CommentItem key={reply.comment_id} comment={reply} onReply={onReply} />
      ))}
    </div>
  );
}

export default function CommentsSection({
  parentId,
  contextType,
  username,
}: CommentsSectionProps) {
  const [comments, setComments] = useState<CommentType[]>([]);
  const [newComment, setNewComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchComments = async () => {
    try {
      const res = await fetch(
        `http://localhost:8000/community/comments?parent_id=${parentId}&context_type=${contextType}`
      );
      if (!res.ok) throw new Error("Failed to fetch comments.");
      const data: CommentType[] = await res.json();
      setComments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  };

  const handleReply = async (
    parent_comment_id: number | null,
    content: string
  ) => {
    if (!content.trim()) return;
    setLoading(true);
    try {
      const payload = {
        parent_id: parentId,
        context_type: contextType,
        username,
        content,
        parent_comment_id,
      };

      const res = await fetch(`http://localhost:8000/community/comments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to post comment.");
      }

      await fetchComments();
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComments();
  }, [parentId, contextType]);

  return (
    <div className="mt-6">
      <h3 className="font-semibold text-gray-900 mb-2">Community Discussion</h3>
      {error && <p className="text-red-600 mb-2">{error}</p>}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Write a comment..."
          className="flex-1 border rounded px-2 py-1 text-black"
        />
        <button
          onClick={() => {
            handleReply(null, newComment);
            setNewComment("");
          }}
          disabled={loading}
          className={`px-4 py-1 rounded text-white ${
            loading ? "bg-gray-400" : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          Post
        </button>
      </div>
      {comments.map((comment) => (
        <CommentItem
          key={comment.comment_id}
          comment={comment}
          onReply={handleReply}
        />
      ))}
    </div>
  );
}

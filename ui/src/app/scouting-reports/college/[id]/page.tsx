import CommentsWrapper from "@/components/comments/comments-wrapper";
import Navigation from "@/components/navigation";

export default function CollegePlayer() {
  const player = { id: "0" };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <Navigation />
      </div>
      {/* Community Discussion */}
      <section className="bg-white shadow rounded-lg p-6 space-y-4">
        <h2 className="text-2xl font-semibold text-black">
          Community Discussion
        </h2>
        <CommentsWrapper
          parentId={Number(player.id)}
          contextType="nba-scouting"
        />
      </section>
    </div>
  );
}

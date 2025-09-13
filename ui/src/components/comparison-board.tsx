"use client";

import {
  DndContext,
  DragEndEvent,
  DragStartEvent,
  DragOverlay,
} from "@dnd-kit/core";
import LineupSlot from "./lineup-builder-slot";
import PlayerCard from "./lineup-builder-card";
import { useEffect, useState } from "react";
import { NBAPlayer } from "@/types/player";

type ComparisonBoardProps = {
  comparison: Record<"Player1" | "Player2", string | null>;
  setComparison: React.Dispatch<
    React.SetStateAction<Record<"Player1" | "Player2", string | null>>
  >;
};

export default function ComparisonBoard({
  comparison,
  setComparison,
}: ComparisonBoardProps) {
  const [players, setPlayers] = useState<NBAPlayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [activeDragId, setActiveDragId] = useState<string | null>(null);

  useEffect(() => {
    async function fetchNBAPlayers() {
      try {
        const res = await fetch("http://localhost:8000/nba/players");
        if (!res.ok)
          throw new Error(`Error fetching NBA players: ${res.status}`);
        const data = await res.json();

        const mappedPlayers: NBAPlayer[] = data.map(
          (p: Record<string, unknown>) => ({
            id: String(p["player_uid"] ?? ""),
            full_name: String(p["full_name"] ?? ""),
            position: String(p["position"] ?? ""),
            height: String(p["height"] ?? ""),
            weight: String(p["weight"] ?? ""),
            team_names: (p["team_names"] as string[]) ?? [],
            college: p["colleges"]
              ? (p["colleges"] as string[]).join(", ")
              : undefined,
            years_pro: p["years_pro"] ? `${p["years_pro"]}` : "Rookie",
            draft_year: p["draft_year"] as number | undefined,
            draft_round: p["draft_round"] as number | undefined,
            draft_pick: p["draft_pick"] as number | undefined,
            stars: (p["stars"] as number) ?? 4,
            overallRating: (p["overallRating"] as number) ?? 85,
            strengths: (p["strengths"] as string[]) ?? [
              "athleticism",
              "defense",
            ],
            weaknesses: (p["weaknesses"] as string[]) ?? ["turnovers"],
            aiAnalysis: String(
              p["aiAnalysis"] ??
                `AI scouting report for ${p["full_name"] ?? ""}.`
            ),
          })
        );

        setPlayers(mappedPlayers);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchNBAPlayers();
  }, []);

  const filteredPlayers = players.filter((p) =>
    p.full_name.toLowerCase().includes(search.toLowerCase())
  );

  const handleDragStart = (event: DragStartEvent) =>
    setActiveDragId(event.active.id.toString());

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveDragId(null);
    if (!over) return;

    const playerId = active.id.toString();
    const target = over.id.toString();

    setComparison((prev) => {
      const updated = { ...prev };

      if (Object.keys(updated).includes(target)) {
        // Remove from any previous slot
        Object.keys(updated).forEach((slot) => {
          if (updated[slot as "Player1" | "Player2"] === playerId) {
            updated[slot as "Player1" | "Player2"] = null;
          }
        });
        updated[target as "Player1" | "Player2"] = playerId;
      } else if (target === "LIBRARY") {
        // Remove player when returned to library
        Object.keys(updated).forEach((slot) => {
          if (updated[slot as "Player1" | "Player2"] === playerId) {
            updated[slot as "Player1" | "Player2"] = null;
          }
        });
      }

      return updated;
    });
  };

  return (
    <DndContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      <div className="flex w-full h-[80vh] gap-6">
        {/* Left: Player library */}
        <div className="w-1/3 flex flex-col bg-white rounded-xl shadow p-4">
          <input
            type="text"
            placeholder="Search players..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full mb-4 rounded-lg border px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none text-black"
          />

          {loading ? (
            <p className="text-gray-600 text-lg">Loading players...</p>
          ) : (
            <div className="flex-1 overflow-y-scroll">
              <div className="grid grid-cols-2 gap-3 text-black">
                {filteredPlayers.map((p) =>
                  !Object.values(comparison).includes(p.id) ? (
                    <PlayerCard
                      key={p.id}
                      id={p.id}
                      name={p.full_name}
                      position={p.position}
                      height={p.height}
                      weight={p.weight}
                      overallRating={p.overallRating}
                      stars={p.stars}
                    />
                  ) : null
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right: Comparison slots */}
        <div className="flex-1 flex flex-row justify-center items-center space-x-10">
          <LineupSlot
            id="Player1"
            playerId={comparison.Player1}
            players={players}
          />
          <LineupSlot
            id="Player2"
            playerId={comparison.Player2}
            players={players}
          />
        </div>
      </div>

      {/* Drag overlay */}
      <DragOverlay>
        {activeDragId &&
          (() => {
            const player = players.find((p) => p.id === activeDragId);
            return player ? (
              <PlayerCard
                id={player.id}
                name={player.full_name}
                position={player.position}
                height={player.height}
                weight={player.weight}
                overallRating={player.overallRating}
                stars={player.stars}
                isOverlay
              />
            ) : null;
          })()}
      </DragOverlay>
    </DndContext>
  );
}

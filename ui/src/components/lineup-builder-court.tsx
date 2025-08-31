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

const positions = ["PG", "SG", "SF", "PF", "C"];

type CourtProps = {
  lineup: Record<string, string | null>; // Mapping of slot -> player ID
  setLineup: React.Dispatch<
    React.SetStateAction<Record<string, string | null>>
  >;
};

export default function Court({ lineup, setLineup }: CourtProps) {
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
            stats: (p["stats"] as NBAPlayer["stats"]) ?? {
              points: 0,
              rebounds: 0,
              assists: 0,
              fieldGoalPercentage: 0,
              threePointPercentage: 0,
              per: 0,
              winShares: 0,
            },
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

  const handleDragStart = (event: DragStartEvent) => {
    setActiveDragId(event.active.id.toString());
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveDragId(null);
    if (!over) return;

    const playerId = active.id.toString();
    const target = over.id.toString();

    setLineup((prev) => {
      const updated = { ...prev };
      if (positions.includes(target)) {
        // Remove player from previous slot
        Object.keys(updated).forEach((pos) => {
          if (updated[pos] === playerId) updated[pos] = null;
        });
        updated[target] = playerId;
      } else if (target === "LIBRARY") {
        Object.keys(updated).forEach((pos) => {
          if (updated[pos] === playerId) updated[pos] = null;
        });
      }
      return updated;
    });
  };

  return (
    <DndContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      <div className="flex flex-col items-center space-y-6 w-full">
        {/* Court */}
        <div className="grid grid-cols-5 gap-6 mb-4">
          {positions.map((pos) => (
            <LineupSlot
              key={pos}
              id={pos}
              playerId={lineup[pos]}
              players={players}
            />
          ))}
        </div>

        {/* Search */}
        <input
          type="text"
          placeholder="Search players..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full max-w-md rounded-lg border px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none text-black mb-4"
        />

        {/* Player library */}
        <LineupSlot id="LIBRARY" playerId={null} players={[]} isLibrary>
          <div className="h-96 w-full overflow-y-scroll rounded-lg border p-2">
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-2">
              {filteredPlayers.map((p) => {
                const inLineup = Object.values(lineup).includes(p.id);
                if (!inLineup) {
                  return (
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
                  );
                }
                return null;
              })}
            </div>
          </div>
        </LineupSlot>

        {/* Drag overlay */}
        <DragOverlay>
          {activeDragId
            ? (() => {
                const player = players.find((p) => p.id === activeDragId);
                if (!player) return null;

                return (
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
                );
              })()
            : null}
        </DragOverlay>
      </div>
    </DndContext>
  );
}

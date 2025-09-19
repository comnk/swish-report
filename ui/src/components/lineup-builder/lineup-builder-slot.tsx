"use client";

import { useDroppable } from "@dnd-kit/core";
import PlayerCard from "./lineup-builder-card";
import { NBAPlayer } from "@/types/player";

type Props = {
  id: string; // "PG" | "SG" | "SF" | "PF" | "C" | "LIBRARY"
  playerId: string | null;
  players: NBAPlayer[];
  isLibrary?: boolean;
  children?: React.ReactNode;
};

export default function LineupSlot({
  id,
  playerId,
  players,
  isLibrary,
  children,
}: Props) {
  const { setNodeRef, isOver } = useDroppable({ id });

  const player = players.find((p) => p.id === playerId);

  return (
    <div
      ref={setNodeRef}
      className={[
        "rounded-xl border-2 bg-gray-100 transition-colors text-black",
        isOver ? "border-blue-500 bg-blue-50" : "border-gray-300",
        isLibrary
          ? "min-h-[8rem] w-full p-3 flex flex-wrap gap-2 overflow-y-auto"
          : "h-36 w-32 flex items-center justify-center",
      ].join(" ")}
    >
      {isLibrary ? (
        children ?? <span className="text-gray-400">Library</span>
      ) : player ? (
        <PlayerCard
          id={player.id}
          name={player.full_name}
          overallRating={player.overallRating}
          position={player.position}
          height={player.height}
          weight={player.weight}
          stars={player.stars}
        />
      ) : (
        <span className="text-gray-400">{id}</span>
      )}
    </div>
  );
}

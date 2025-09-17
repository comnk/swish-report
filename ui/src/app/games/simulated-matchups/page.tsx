"use client";

import { useState } from "react";
import { DndContext, useDraggable, useDroppable } from "@dnd-kit/core";
import Navigation from "@/components/navigation";

interface Player {
  id: number;
  name: string;
  position: string;
  rating: number;
}

// Example pool of players
const availablePlayers: Player[] = [
  { id: 1, name: "LeBron James", position: "SF", rating: 95 },
  { id: 2, name: "Stephen Curry", position: "PG", rating: 93 },
  { id: 3, name: "Kevin Durant", position: "PF", rating: 94 },
  { id: 4, name: "Giannis Antetokounmpo", position: "PF", rating: 96 },
  { id: 5, name: "Jayson Tatum", position: "SF", rating: 91 },
  { id: 6, name: "Joel Embiid", position: "C", rating: 94 },
];

function DraggablePlayer({ player }: { player: Player }) {
  const { attributes, listeners, setNodeRef, transform } = useDraggable({
    id: `player-${player.id}`,
  });

  const style = {
    transform: transform
      ? `translate3d(${transform.x}px, ${transform.y}px, 0)`
      : undefined,
  };

  return (
    <div
      ref={setNodeRef}
      {...listeners}
      {...attributes}
      className="p-2 m-1 bg-blue-100 rounded-lg cursor-grab hover:bg-blue-200"
      style={style}
    >
      {player.name} ({player.position}) - {player.rating}
    </div>
  );
}

function DroppableTeam({
  teamName,
  players,
  onDrop,
}: {
  teamName: string;
  players: Player[];
  onDrop: (playerId: number) => void;
}) {
  const { setNodeRef } = useDroppable({
    id: teamName,
  });

  return (
    <div
      ref={setNodeRef}
      className="min-h-[200px] p-4 border-2 border-dashed border-gray-300 rounded-lg"
    >
      <h2 className="font-bold mb-2">{teamName}</h2>
      {players.length === 0 ? (
        <p className="text-gray-400">Drop players here</p>
      ) : (
        players.map((p) => (
          <div key={p.id} className="p-2 m-1 bg-green-100 rounded-lg">
            {p.name} ({p.position}) - {p.rating}
          </div>
        ))
      )}
    </div>
  );
}

export default function SimulatedMatchupForm() {
  const [teamAPlayers, setTeamAPlayers] = useState<Player[]>([]);
  const [teamBPlayers, setTeamBPlayers] = useState<Player[]>([]);
  const [result, setResult] = useState<string | null>(null);

  const handleDragEnd = (event: any) => {
    const { active, over } = event;
    if (!over) return;

    const playerId = Number(active.id.split("-")[1]);
    const player = availablePlayers.find((p) => p.id === playerId);
    if (!player) return;

    if (over.id === "Team A") {
      if (!teamAPlayers.some((p) => p.id === player.id)) {
        setTeamAPlayers([...teamAPlayers, player]);
      }
    } else if (over.id === "Team B") {
      if (!teamBPlayers.some((p) => p.id === player.id)) {
        setTeamBPlayers([...teamBPlayers, player]);
      }
    }
  };

  const simulateMatchup = () => {
    const scoreA = teamAPlayers.reduce((acc, p) => acc + p.rating, 0);
    const scoreB = teamBPlayers.reduce((acc, p) => acc + p.rating, 0);
    setResult(`Team A: ${scoreA} - ${scoreB} :Team B`);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <Navigation />
      <div className="max-w-5xl mx-auto mt-10 bg-white p-8 rounded-2xl shadow-lg">
        <h1 className="text-2xl font-bold mb-6 text-center">
          Simulated Matchup
        </h1>

        <DndContext onDragEnd={handleDragEnd}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Available players */}
            <div>
              <h2 className="font-bold mb-2">Available Players</h2>
              <div className="p-2 border rounded-lg min-h-[200px]">
                {availablePlayers.map((p) => (
                  <DraggablePlayer key={p.id} player={p} />
                ))}
              </div>
            </div>

            {/* Team A */}
            <DroppableTeam
              teamName="Team A"
              players={teamAPlayers}
              onDrop={() => {}}
            />

            {/* Team B */}
            <DroppableTeam
              teamName="Team B"
              players={teamBPlayers}
              onDrop={() => {}}
            />
          </div>
        </DndContext>

        <button
          onClick={simulateMatchup}
          className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition"
        >
          Simulate Matchup
        </button>

        {result && (
          <div className="mt-6 p-4 bg-gray-100 rounded-lg text-center font-medium">
            {result}
          </div>
        )}
      </div>
    </main>
  );
}

import { HighSchoolPlayer } from "@/types/player";

interface PlayerPageProps {
  params: { id: string }; // already unwrapped in server component
}

export default async function PlayerPage({ params }: PlayerPageProps) {
    const { id } = await params;

    // Fetch directly on the server
    const res = await fetch(`http://localhost:8000/high-school/prospects/${id}`, {
        cache: "no-store",
    });

    if (!res.ok) {
        throw new Error(`Failed to fetch player: ${res.status}`);
    }

    const player: HighSchoolPlayer = await res.json();

    return (
        <main className="p-6">
            <h1 className="text-3xl font-bold">{player.name}</h1>
            <p>Position: {player.position}</p>
            <p>School: {player.school}</p>
        </main>
    );
}

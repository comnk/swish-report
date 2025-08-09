import { notFound } from "next/navigation";

interface PlayerPageProps {
    params: { id: string };
}

export default async function PlayerPage({ params }: PlayerPageProps) {
    const { id } = params;

    // Fetch player data from your backend
    const res = await fetch(`http://localhost:8000/prospects/highschool/${id}`);
    if (!res.ok) return notFound();

    const player = await res.json();

    return (
        <main className="p-6">
        <h1 className="text-3xl font-bold">{player.full_name}</h1>
        <p>Position: {player.position}</p>
        <p>School: {player.school_name}</p>
        {/* More details here */}
        </main>
    );
}

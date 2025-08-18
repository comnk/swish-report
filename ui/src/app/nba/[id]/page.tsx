interface PlayerPageProps {
  params: { id: string }; // already unwrapped in server component
}

export default async function PlayerPage({ params }: PlayerPageProps) {
    return (
        <div>
            HELLO!
        </div>
    )
}
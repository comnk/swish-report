"use client";

import { useDraggable } from "@dnd-kit/core";

type Props = {
  id: string;
  name: string;
  overallRating: number;
  position: string;
  height: string;
  weight: string;
  stars: number;
  isOverlay?: boolean;
};

export default function PlayerCard({
  id,
  name,
  overallRating,
  position,
  height,
  weight,
  stars,
  isOverlay = false,
}: Props) {
  const { attributes, listeners, setNodeRef, transform, isDragging } =
    useDraggable({ id });

  const style: React.CSSProperties = {
    transform:
      isDragging && transform
        ? `translate3d(${transform.x}px, ${transform.y}px, 0)`
        : undefined,
    opacity: isDragging ? 0.6 : 1,
    position: isOverlay ? "absolute" : "relative",
    zIndex: isOverlay ? 50 : "auto",
    width: "100%", // maintain width in grid
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="cursor-grab rounded-lg border bg-white p-3 shadow-md flex flex-col justify-between gap-1 text-sm break-words"
    >
      <div className="font-semibold text-center break-words">{name}</div>
      <div className="text-xs text-gray-500 text-center">{position}</div>
      <div className="flex justify-center items-center gap-2 text-xs text-gray-700 mt-1">
        <span>⭐ {stars}</span>
        <span>OVR: {overallRating}</span>
      </div>
      <div className="text-xs text-gray-500 text-center mt-1">
        {height} | {weight}
      </div>
    </div>
  );
}

import { renameParticipant } from "@/lib/api/participants";
import { Participant } from "@/lib/types/participant";
import { Check, Pencil } from "lucide-react";
import React, { useMemo, useState } from "react";

interface Props {
  battleId: number;
  team: number;
  paricipants: { value: Participant[]; onChange: (v: Participant[]) => void };
}

export default function Team({
  paricipants: iparticipants,
  team,
  battleId,
}: Props) {
  const [editingParticipantId, setEditingParticipantId] = useState<
    number | null
  >(null);
  const [editName, setEditName] = useState("");

  const participants = useMemo(() => {
    return iparticipants.value.filter((p) => p.teamNumber === team);
  }, [iparticipants.value, team]);

  const handleStartEditingParticipant = (p: Participant) => {
    setEditingParticipantId(p.id);
    setEditName(p.name);
  };

  const handleConfirmRename = async (participantId: number) => {
    const trimmed = editName.trim();
    if (
      !trimmed ||
      trimmed === participants.find((p) => p.id === participantId)?.name
    ) {
      setEditingParticipantId(null);
      return;
    }

    try {
      const updated = await renameParticipant(battleId, participantId, trimmed);

      iparticipants.onChange(
        iparticipants.value.map((p) =>
          p.id === participantId
            ? {
                ...p,
                name: updated.mc_name,
                avatar: updated.mc_name.charAt(0).toUpperCase(),
              }
            : p,
        ),
      );
    } catch {
      // Silently fail
    }

    setEditingParticipantId(null);
  };

  return (
    <div className="flex items-center gap-2">
      <div className="flex -space-x-1">
        {participants.map((p) => (
          <div
            key={p.id}
            className="flex h-8 w-8 items-center justify-center rounded-full bg-mc1/20 text-sm font-black text-mc1 ring-1 ring-mc1/30"
          >
            {p.avatar}
          </div>
        ))}
      </div>

      <div className="flex items-center gap-1">
        {participants.map((p, i) => (
          <span key={p.id} className="flex items-center">
            {i > 0 && <span className="mx-0.5 text-muted-foreground">&</span>}

            {editingParticipantId === p.id ? (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleConfirmRename(p.id);
                }}
                className="inline-flex items-center gap-1"
              >
                <input
                  autoFocus
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  onBlur={() => {
                    handleConfirmRename(p.id);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Escape") {
                      setEditingParticipantId(null);
                    }
                  }}
                  className="h-6 w-28 rounded border border-primary bg-background px-1.5 text-sm font-bold text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                />

                <button type="submit" className="text-primary">
                  <Check className="h-3.5 w-3.5" />
                </button>
              </form>
            ) : (
              <button
                onClick={() => handleStartEditingParticipant(p)}
                className="group/edit flex items-center gap-1 text-sm font-bold text-foreground transition-colors hover:text-primary"
              >
                {p.name}
                <Pencil className="h-3 w-3 opacity-0 transition-opacity group-hover/edit:opacity-60" />
              </button>
            )}
          </span>
        ))}
      </div>
    </div>
  );
}

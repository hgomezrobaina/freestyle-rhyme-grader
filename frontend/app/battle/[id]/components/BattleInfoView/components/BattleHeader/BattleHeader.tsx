import { Battle } from "@/lib/types/battle";
import React from "react";

interface Props {
  battle: Battle;
}

export default function BattleHeader({ battle }: Props) {
  return (
    <div>
      <h1 className="text-xl font-black uppercase tracking-tight text-foreground sm:text-2xl">
        {battle.title}
      </h1>

      {battle.event && (
        <p className="mt-1 text-sm text-muted-foreground">{battle.event}</p>
      )}
    </div>
  );
}

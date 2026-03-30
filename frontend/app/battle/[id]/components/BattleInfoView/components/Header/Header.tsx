import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import React from "react";

export default function Header() {
  return (
    <Button
      asChild
      variant="ghost"
      size="sm"
      className="w-fit text-muted-foreground"
    >
      <Link href="/">
        <ArrowLeft className="h-4 w-4" />
        Volver a batallas
      </Link>
    </Button>
  );
}

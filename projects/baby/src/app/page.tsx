"use client";

import Link from "next/link";
import { Badge, Card, PageHeader, Stat } from "@/components/ui";
import { NAMES_SEED, NURSERY_SEED, REGISTRY_SEED } from "@/lib/seed";
import { useCollection } from "@/lib/useCollection";
import { money } from "@/lib/format";
import type { NameCandidate, NurseryTask, RegistryItem } from "@/lib/types";

const SETTLED = ["registered", "purchased", "received"];

export default function OverviewPage() {
  const registry = useCollection<RegistryItem>("registry", REGISTRY_SEED);
  const names = useCollection<NameCandidate>("names", NAMES_SEED);
  const nursery = useCollection<NurseryTask>("nursery", NURSERY_SEED);

  const openMusts = registry.rows.filter(
    (r) =>
      r.priority === "must" &&
      !SETTLED.includes(r.status) &&
      r.status !== "passed",
  );
  const estimate = registry.rows
    .filter((r) => r.status !== "passed")
    .reduce((sum, r) => sum + (r.priceCents ?? 0), 0);
  const shortlist = names.rows.filter((n) => n.list === "shortlist");
  const tasksLeft = nursery.rows.filter((t) => t.status !== "done");

  return (
    <>
      <PageHeader
        title="Overview"
        subtitle="Where things stand across the registry, the name list, and the nursery."
      />

      <div className="mb-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat label="Must-haves open" value={openMusts.length} />
        <Stat label="Registry estimate" value={estimate ? money(estimate) : "—"} />
        <Stat label="Names shortlisted" value={shortlist.length} />
        <Stat label="Nursery tasks left" value={tasksLeft.length} />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-medium">Next up on the registry</h2>
            <Link href="/registry" className="text-sm text-sage underline underline-offset-4">
              Open
            </Link>
          </div>
          {openMusts.length === 0 ? (
            <p className="text-sm text-muted">Every must-have is settled.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {openMusts.slice(0, 6).map((r) => (
                <li key={r.id} className="flex items-center justify-between gap-3">
                  <span>{r.name}</span>
                  <Badge>{r.status}</Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-medium">Nursery, in progress</h2>
            <Link href="/nursery" className="text-sm text-sage underline underline-offset-4">
              Open
            </Link>
          </div>
          {tasksLeft.length === 0 ? (
            <p className="text-sm text-muted">The room is done.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {tasksLeft.slice(0, 6).map((t) => (
                <li key={t.id} className="flex items-center justify-between gap-3">
                  <span>{t.title}</span>
                  <Badge tone={t.status === "doing" ? "sage" : "neutral"}>
                    {t.status}
                  </Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-medium">Shortlisted names</h2>
            <Link href="/names" className="text-sm text-sage underline underline-offset-4">
              Open
            </Link>
          </div>
          {shortlist.length === 0 ? (
            <p className="text-sm text-muted">
              Nothing shortlisted yet — rate a few candidates and move the winners up.
            </p>
          ) : (
            <ul className="flex flex-wrap gap-2 text-sm">
              {shortlist.map((n) => (
                <li key={n.id}>
                  <Badge tone="sage">{n.name}</Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card className="border-l-4 border-l-clay">
          <h2 className="mb-2 font-medium">Coming in phase 2: tracker</h2>
          <p className="text-sm text-muted">
            Feeds, sleep, diapers, and growth logging. The data model is already
            defined in <code className="text-ink">src/lib/types.ts</code>; it needs a
            real database and a fast mobile logging screen before it is worth
            shipping.
          </p>
        </Card>
      </div>

      <p className="mt-8 text-xs text-muted">
        Data is stored locally in this browser. It is not synced between devices
        yet — that lands with phase 2.
      </p>
    </>
  );
}

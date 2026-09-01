"use client";

import { useMemo, useState } from "react";
import {
  Badge,
  Button,
  Card,
  Empty,
  PageHeader,
  SelectField,
  Stat,
  TextField,
} from "@/components/ui";
import { REGISTRY_SEED } from "@/lib/seed";
import { useCollection } from "@/lib/useCollection";
import { dollarsToCents, money, titleCase } from "@/lib/format";
import {
  REGISTRY_CATEGORIES,
  REGISTRY_STATUSES,
  type Priority,
  type RegistryCategory,
  type RegistryItem,
  type RegistryStatus,
} from "@/lib/types";

const PRIORITIES: Priority[] = ["must", "nice", "maybe"];
const PRIORITY_TONE: Record<Priority, "sage" | "clay" | "neutral"> = {
  must: "clay",
  nice: "sage",
  maybe: "neutral",
};

/** Anything past "decided" counts as settled for the progress stat. */
const SETTLED: RegistryStatus[] = ["registered", "purchased", "received"];

export default function RegistryPage() {
  const { rows, add, update, remove } = useCollection<RegistryItem>(
    "registry",
    REGISTRY_SEED,
  );

  const [category, setCategory] = useState<RegistryCategory | "all">("all");
  const [status, setStatus] = useState<RegistryStatus | "all">("all");
  const [draft, setDraft] = useState({
    name: "",
    category: "sleep" as RegistryCategory,
    priority: "must" as Priority,
    price: "",
    url: "",
  });

  const visible = useMemo(
    () =>
      rows.filter(
        (r) =>
          (category === "all" || r.category === category) &&
          (status === "all" || r.status === status),
      ),
    [rows, category, status],
  );

  const grouped = useMemo(() => {
    const map = new Map<RegistryCategory, RegistryItem[]>();
    for (const r of visible) {
      const list = map.get(r.category) ?? [];
      list.push(r);
      map.set(r.category, list);
    }
    return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]));
  }, [visible]);

  const settledCount = rows.filter((r) => SETTLED.includes(r.status)).length;
  const openMusts = rows.filter(
    (r) => r.priority === "must" && !SETTLED.includes(r.status) && r.status !== "passed",
  ).length;
  const estimate = rows
    .filter((r) => r.status !== "passed")
    .reduce((sum, r) => sum + (r.priceCents ?? 0), 0);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const name = draft.name.trim();
    if (!name) return;
    add({
      name,
      category: draft.category,
      priority: draft.priority,
      status: "researching",
      priceCents: dollarsToCents(draft.price),
      url: draft.url.trim() || undefined,
    } as Omit<RegistryItem, "id" | "createdAt">);
    setDraft({ ...draft, name: "", price: "", url: "" });
  }

  return (
    <>
      <PageHeader
        title="Registry"
        subtitle="Generic gear slots you research into. Edit anything — this is your list, not a recommendation."
      />

      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat label="Items" value={rows.length} />
        <Stat label="Settled" value={`${settledCount}/${rows.length}`} />
        <Stat label="Must-haves open" value={openMusts} />
        <Stat label="Est. total" value={estimate ? money(estimate) : "—"} />
      </div>

      <Card className="mb-6">
        <form onSubmit={submit} className="flex flex-wrap items-end gap-2">
          <label className="flex min-w-48 flex-1 flex-col gap-1 text-sm">
            <span className="text-muted">Item</span>
            <TextField
              value={draft.name}
              onChange={(e) => setDraft({ ...draft, name: e.target.value })}
              placeholder="White noise machine"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Category</span>
            <SelectField
              value={draft.category}
              onChange={(e) =>
                setDraft({ ...draft, category: e.target.value as RegistryCategory })
              }
            >
              {REGISTRY_CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {titleCase(c)}
                </option>
              ))}
            </SelectField>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Priority</span>
            <SelectField
              value={draft.priority}
              onChange={(e) =>
                setDraft({ ...draft, priority: e.target.value as Priority })
              }
            >
              {PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {titleCase(p)}
                </option>
              ))}
            </SelectField>
          </label>
          <label className="flex w-28 flex-col gap-1 text-sm">
            <span className="text-muted">Price</span>
            <TextField
              value={draft.price}
              onChange={(e) => setDraft({ ...draft, price: e.target.value })}
              placeholder="$0"
              inputMode="decimal"
            />
          </label>
          <label className="flex min-w-40 flex-1 flex-col gap-1 text-sm">
            <span className="text-muted">Link</span>
            <TextField
              value={draft.url}
              onChange={(e) => setDraft({ ...draft, url: e.target.value })}
              placeholder="https://"
              type="url"
            />
          </label>
          <Button type="submit">Add</Button>
        </form>
      </Card>

      <div className="mb-4 flex flex-wrap gap-2">
        <SelectField
          value={category}
          onChange={(e) =>
            setCategory(e.target.value as RegistryCategory | "all")
          }
          aria-label="Filter by category"
        >
          <option value="all">All categories</option>
          {REGISTRY_CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {titleCase(c)}
            </option>
          ))}
        </SelectField>
        <SelectField
          value={status}
          onChange={(e) => setStatus(e.target.value as RegistryStatus | "all")}
          aria-label="Filter by status"
        >
          <option value="all">All statuses</option>
          {REGISTRY_STATUSES.map((s) => (
            <option key={s} value={s}>
              {titleCase(s)}
            </option>
          ))}
        </SelectField>
      </div>

      {grouped.length === 0 ? (
        <Empty>Nothing matches those filters.</Empty>
      ) : (
        <div className="space-y-6">
          {grouped.map(([cat, items]) => (
            <section key={cat}>
              <h2 className="mb-2 text-sm font-medium tracking-wide text-muted uppercase">
                {titleCase(cat)}
              </h2>
              <ul className="space-y-2">
                {items.map((r) => (
                  <li key={r.id}>
                    <Card className="flex flex-wrap items-center gap-3">
                      <div className="min-w-48 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          {r.url ? (
                            <a
                              href={r.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="font-medium underline decoration-line underline-offset-4 hover:decoration-sage"
                            >
                              {r.name}
                            </a>
                          ) : (
                            <span className="font-medium">{r.name}</span>
                          )}
                          <Badge tone={PRIORITY_TONE[r.priority]}>
                            {r.priority}
                          </Badge>
                        </div>
                        {r.notes && (
                          <p className="mt-1 text-sm text-muted">{r.notes}</p>
                        )}
                      </div>
                      <span className="tabular-nums text-sm text-muted">
                        {money(r.priceCents)}
                      </span>
                      <SelectField
                        value={r.status}
                        onChange={(e) =>
                          update(r.id, {
                            status: e.target.value as RegistryStatus,
                          })
                        }
                        aria-label={`Status for ${r.name}`}
                      >
                        {REGISTRY_STATUSES.map((s) => (
                          <option key={s} value={s}>
                            {titleCase(s)}
                          </option>
                        ))}
                      </SelectField>
                      <Button
                        variant="danger"
                        onClick={() => remove(r.id)}
                        aria-label={`Remove ${r.name}`}
                      >
                        Remove
                      </Button>
                    </Card>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      )}
    </>
  );
}

"use client";

import { useMemo, useState } from "react";
import {
  Badge,
  Button,
  Card,
  Empty,
  PageHeader,
  SelectField,
  TextField,
} from "@/components/ui";
import { Rating } from "@/components/Rating";
import { NAMES_SEED, VOTERS } from "@/lib/seed";
import { useCollection } from "@/lib/useCollection";
import { titleCase } from "@/lib/format";
import {
  NAME_LISTS,
  type NameCandidate,
  type NameList,
  type NameStyle,
  type Voter,
} from "@/lib/types";

const STYLES: NameStyle[] = ["girl", "boy", "neutral"];

/** Sum of every rating cast. Unrated names sink to the bottom, which is right. */
function score(n: NameCandidate) {
  return Object.values(n.ratings).reduce((a, b) => a + b, 0);
}

export default function NamesPage() {
  const names = useCollection<NameCandidate>("names", NAMES_SEED);
  const voters = useCollection<Voter>("voters", VOTERS);

  const [list, setList] = useState<NameList | "all">("all");
  const [style, setStyle] = useState<NameStyle | "all">("all");
  const [draft, setDraft] = useState({ name: "", style: "neutral" as NameStyle });

  const visible = useMemo(
    () =>
      names.rows
        .filter(
          (n) =>
            (list === "all" || n.list === list) &&
            (style === "all" || n.style === style),
        )
        .sort((a, b) => score(b) - score(a) || a.name.localeCompare(b.name)),
    [names.rows, list, style],
  );

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const name = draft.name.trim();
    if (!name) return;
    names.add({
      name,
      style: draft.style,
      list: "longlist",
      ratings: {},
    } as Omit<NameCandidate, "id" | "createdAt">);
    setDraft({ ...draft, name: "" });
  }

  function rate(n: NameCandidate, voterId: string, value: number) {
    names.update(n.id, { ratings: { ...n.ratings, [voterId]: value } });
  }

  return (
    <>
      <PageHeader
        title="Names"
        subtitle="Everyone rates independently. Highest combined score floats to the top — no arguing required."
      />

      <Card className="mb-6">
        <form onSubmit={submit} className="flex flex-wrap items-end gap-2">
          <label className="flex min-w-48 flex-1 flex-col gap-1 text-sm">
            <span className="text-muted">Name</span>
            <TextField
              value={draft.name}
              onChange={(e) => setDraft({ ...draft, name: e.target.value })}
              placeholder="Add a candidate"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Style</span>
            <SelectField
              value={draft.style}
              onChange={(e) =>
                setDraft({ ...draft, style: e.target.value as NameStyle })
              }
            >
              {STYLES.map((s) => (
                <option key={s} value={s}>
                  {titleCase(s)}
                </option>
              ))}
            </SelectField>
          </label>
          <Button type="submit">Add</Button>
        </form>
      </Card>

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <SelectField
          value={list}
          onChange={(e) => setList(e.target.value as NameList | "all")}
          aria-label="Filter by list"
        >
          <option value="all">All lists</option>
          {NAME_LISTS.map((l) => (
            <option key={l} value={l}>
              {titleCase(l)}
            </option>
          ))}
        </SelectField>
        <SelectField
          value={style}
          onChange={(e) => setStyle(e.target.value as NameStyle | "all")}
          aria-label="Filter by style"
        >
          <option value="all">All styles</option>
          {STYLES.map((s) => (
            <option key={s} value={s}>
              {titleCase(s)}
            </option>
          ))}
        </SelectField>

        <div className="ml-auto flex flex-wrap items-center gap-2 text-sm text-muted">
          <span>Voters:</span>
          {voters.rows.map((v) => (
            <TextField
              key={v.id}
              value={v.label}
              onChange={(e) => voters.update(v.id, { label: e.target.value })}
              aria-label={`Name of voter ${v.label}`}
              className="w-28"
            />
          ))}
        </div>
      </div>

      {visible.length === 0 ? (
        <Empty>No names on this list yet.</Empty>
      ) : (
        <ul className="space-y-2">
          {visible.map((n) => (
            <li key={n.id}>
              <Card className="flex flex-wrap items-center gap-x-4 gap-y-3">
                <div className="min-w-44 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-lg font-medium">{n.name}</span>
                    <Badge tone={n.list === "shortlist" ? "sage" : "neutral"}>
                      {n.style}
                    </Badge>
                  </div>
                  {(n.origin || n.meaning) && (
                    <p className="mt-0.5 text-sm text-muted">
                      {[n.origin, n.meaning].filter(Boolean).join(" · ")}
                    </p>
                  )}
                </div>

                <div className="flex flex-wrap gap-x-5 gap-y-2">
                  {voters.rows.map((v) => (
                    <div key={v.id} className="flex flex-col gap-1">
                      <span className="text-xs text-muted">{v.label}</span>
                      <Rating
                        label={`${v.label} rating for ${n.name}`}
                        value={n.ratings[v.id] ?? 0}
                        onChange={(next) => rate(n, v.id, next)}
                      />
                    </div>
                  ))}
                </div>

                <span className="w-8 text-right tabular-nums text-sm text-muted">
                  {score(n) || "—"}
                </span>

                <SelectField
                  value={n.list}
                  onChange={(e) =>
                    names.update(n.id, { list: e.target.value as NameList })
                  }
                  aria-label={`List for ${n.name}`}
                >
                  {NAME_LISTS.map((l) => (
                    <option key={l} value={l}>
                      {titleCase(l)}
                    </option>
                  ))}
                </SelectField>

                <Button
                  variant="danger"
                  onClick={() => names.remove(n.id)}
                  aria-label={`Remove ${n.name}`}
                >
                  Remove
                </Button>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

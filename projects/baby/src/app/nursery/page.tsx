"use client";

import { useMemo, useState } from "react";
import {
  Button,
  Card,
  Empty,
  PageHeader,
  SelectField,
  Stat,
  TextField,
} from "@/components/ui";
import { NURSERY_SEED } from "@/lib/seed";
import { useCollection } from "@/lib/useCollection";
import { titleCase } from "@/lib/format";
import {
  NURSERY_AREAS,
  type NurseryArea,
  type NurseryTask,
  type TaskStatus,
} from "@/lib/types";

const NEXT_STATUS: Record<TaskStatus, TaskStatus> = {
  todo: "doing",
  doing: "done",
  done: "todo",
};

export default function NurseryPage() {
  const { rows, add, update, remove } = useCollection<NurseryTask>(
    "nursery",
    NURSERY_SEED,
  );

  const [area, setArea] = useState<NurseryArea | "all">("all");
  const [hideDone, setHideDone] = useState(false);
  const [draft, setDraft] = useState({
    title: "",
    area: "logistics" as NurseryArea,
    due: "",
  });

  const visible = useMemo(
    () =>
      rows.filter(
        (t) =>
          (area === "all" || t.area === area) &&
          !(hideDone && t.status === "done"),
      ),
    [rows, area, hideDone],
  );

  const grouped = useMemo(() => {
    const map = new Map<NurseryArea, NurseryTask[]>();
    for (const t of visible) {
      const list = map.get(t.area) ?? [];
      list.push(t);
      map.set(t.area, list);
    }
    return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]));
  }, [visible]);

  const done = rows.filter((t) => t.status === "done").length;
  const doing = rows.filter((t) => t.status === "doing").length;

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const title = draft.title.trim();
    if (!title) return;
    add({
      title,
      area: draft.area,
      status: "todo",
      due: draft.due || undefined,
    } as Omit<NurseryTask, "id" | "createdAt">);
    setDraft({ ...draft, title: "", due: "" });
  }

  return (
    <>
      <PageHeader
        title="Nursery"
        subtitle="Setup checklist by area. Click a status to advance it."
      />

      <div className="mb-6 grid grid-cols-3 gap-3">
        <Stat label="Tasks" value={rows.length} />
        <Stat label="In progress" value={doing} />
        <Stat label="Done" value={`${done}/${rows.length}`} />
      </div>

      <Card className="mb-6">
        <form onSubmit={submit} className="flex flex-wrap items-end gap-2">
          <label className="flex min-w-48 flex-1 flex-col gap-1 text-sm">
            <span className="text-muted">Task</span>
            <TextField
              value={draft.title}
              onChange={(e) => setDraft({ ...draft, title: e.target.value })}
              placeholder="Hang the shelf"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Area</span>
            <SelectField
              value={draft.area}
              onChange={(e) =>
                setDraft({ ...draft, area: e.target.value as NurseryArea })
              }
            >
              {NURSERY_AREAS.map((a) => (
                <option key={a} value={a}>
                  {titleCase(a)}
                </option>
              ))}
            </SelectField>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">By</span>
            <TextField
              type="date"
              value={draft.due}
              onChange={(e) => setDraft({ ...draft, due: e.target.value })}
            />
          </label>
          <Button type="submit">Add</Button>
        </form>
      </Card>

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <SelectField
          value={area}
          onChange={(e) => setArea(e.target.value as NurseryArea | "all")}
          aria-label="Filter by area"
        >
          <option value="all">All areas</option>
          {NURSERY_AREAS.map((a) => (
            <option key={a} value={a}>
              {titleCase(a)}
            </option>
          ))}
        </SelectField>
        <label className="flex items-center gap-2 text-sm text-muted">
          <input
            type="checkbox"
            checked={hideDone}
            onChange={(e) => setHideDone(e.target.checked)}
            className="accent-sage"
          />
          Hide done
        </label>
      </div>

      {grouped.length === 0 ? (
        <Empty>Nothing left here.</Empty>
      ) : (
        <div className="space-y-6">
          {grouped.map(([a, tasks]) => (
            <section key={a}>
              <h2 className="mb-2 text-sm font-medium tracking-wide text-muted uppercase">
                {titleCase(a)}
              </h2>
              <ul className="space-y-2">
                {tasks.map((t) => (
                  <li key={t.id}>
                    <Card className="flex flex-wrap items-center gap-3">
                      <Button
                        variant="ghost"
                        onClick={() =>
                          update(t.id, { status: NEXT_STATUS[t.status] })
                        }
                        aria-label={`Advance status of ${t.title} (currently ${t.status})`}
                        className="w-24 shrink-0"
                      >
                        {titleCase(t.status)}
                      </Button>
                      <div className="min-w-48 flex-1">
                        <span
                          className={
                            t.status === "done"
                              ? "text-muted line-through"
                              : "font-medium"
                          }
                        >
                          {t.title}
                        </span>
                        {t.notes && (
                          <p className="mt-1 text-sm text-muted">{t.notes}</p>
                        )}
                      </div>
                      {t.due && (
                        <span className="tabular-nums text-sm text-muted">
                          {t.due}
                        </span>
                      )}
                      <Button
                        variant="danger"
                        onClick={() => remove(t.id)}
                        aria-label={`Remove ${t.title}`}
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

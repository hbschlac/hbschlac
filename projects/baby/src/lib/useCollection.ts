"use client";

import { useCallback, useEffect, useState } from "react";
import { adapter, newId } from "./storage";

interface Row {
  id: string;
}

/**
 * A persisted list of rows.
 *
 * Renders the seed on the server and during the first client paint, then
 * replaces it with saved data on mount — so there is no hydration mismatch and
 * no empty flash.
 */
export function useCollection<T extends Row>(collection: string, seed: T[]) {
  const [rows, setRows] = useState<T[]>(seed);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let active = true;
    adapter.read<T>(collection).then((saved) => {
      if (!active) return;
      if (saved) setRows(saved);
      setLoaded(true);
    });
    return () => {
      active = false;
    };
  }, [collection]);

  // Only persist after the initial read has landed, otherwise the seed would
  // overwrite saved data on every page load.
  const commit = useCallback(
    (next: T[]) => {
      setRows(next);
      if (loaded) void adapter.write(collection, next);
    },
    [collection, loaded],
  );

  const add = useCallback(
    (row: Omit<T, "id" | "createdAt"> & Partial<Pick<T, "id">>) => {
      const created = {
        ...row,
        id: row.id ?? newId(),
        createdAt: new Date().toISOString(),
      } as unknown as T;
      commit([created, ...rows]);
      return created;
    },
    [commit, rows],
  );

  const update = useCallback(
    (id: string, patch: Partial<T>) => {
      commit(rows.map((r) => (r.id === id ? { ...r, ...patch } : r)));
    },
    [commit, rows],
  );

  const remove = useCallback(
    (id: string) => {
      commit(rows.filter((r) => r.id !== id));
    },
    [commit, rows],
  );

  const reset = useCallback(() => commit(seed), [commit, seed]);

  return { rows, loaded, add, update, remove, reset };
}

import type { ID } from "./types";

/**
 * Everything the app needs from persistence. Phase 1 ships the localStorage
 * adapter below; phase 2 swaps in an HTTP adapter backed by a real database
 * without any page or component changing.
 */
export interface StorageAdapter {
  read<T>(collection: string): Promise<T[] | null>;
  write<T>(collection: string, rows: T[]): Promise<void>;
}

const PREFIX = "baby:v1:";

export const localAdapter: StorageAdapter = {
  async read<T>(collection: string) {
    if (typeof window === "undefined") return null;
    try {
      const raw = window.localStorage.getItem(PREFIX + collection);
      return raw ? (JSON.parse(raw) as T[]) : null;
    } catch {
      // Corrupt or blocked storage reads as "nothing saved yet" rather than
      // taking the page down.
      return null;
    }
  },
  async write<T>(collection: string, rows: T[]) {
    if (typeof window === "undefined") return;
    try {
      window.localStorage.setItem(PREFIX + collection, JSON.stringify(rows));
    } catch {
      // Quota or private-mode failures are non-fatal: the in-memory state is
      // still correct for this session.
    }
  },
};

export const adapter: StorageAdapter = localAdapter;

export function newId(): ID {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

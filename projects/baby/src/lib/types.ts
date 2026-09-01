// Domain types for Baby.
//
// Phase 1 (shipped): registry, names, nursery.
// Phase 2 (planned): tracker — feeds, sleep, diapers, growth. Those types live at
// the bottom of this file so the storage layer and the eventual API share one
// vocabulary instead of being retrofitted later.

export type ID = string;

/* ---------------------------------- Registry --------------------------------- */

export const REGISTRY_CATEGORIES = [
  "sleep",
  "feeding",
  "diapering",
  "clothing",
  "travel",
  "bath",
  "play",
  "health",
  "postpartum",
  "nursery",
] as const;
export type RegistryCategory = (typeof REGISTRY_CATEGORIES)[number];

export const REGISTRY_STATUSES = [
  "researching",
  "decided",
  "registered",
  "purchased",
  "received",
  "passed",
] as const;
export type RegistryStatus = (typeof REGISTRY_STATUSES)[number];

export type Priority = "must" | "nice" | "maybe";

export interface RegistryItem {
  id: ID;
  name: string;
  category: RegistryCategory;
  status: RegistryStatus;
  priority: Priority;
  /** Stored in cents to avoid float drift. */
  priceCents?: number;
  brand?: string;
  url?: string;
  notes?: string;
  createdAt: string;
}

/* ----------------------------------- Names ----------------------------------- */

export const NAME_LISTS = ["longlist", "shortlist", "vetoed"] as const;
export type NameList = (typeof NAME_LISTS)[number];

export type NameStyle = "girl" | "boy" | "neutral";

export interface NameCandidate {
  id: ID;
  name: string;
  style: NameStyle;
  list: NameList;
  origin?: string;
  meaning?: string;
  /** 0 = unrated, 1-5 otherwise. Keyed by voter id so more voters can be added. */
  ratings: Record<string, number>;
  notes?: string;
  createdAt: string;
}

/** Voters are data, not hardcoded columns — add a grandparent without a migration. */
export interface Voter {
  id: string;
  label: string;
}

/* ---------------------------------- Nursery ---------------------------------- */

export const NURSERY_AREAS = [
  "furniture",
  "storage",
  "decor",
  "safety",
  "textiles",
  "logistics",
] as const;
export type NurseryArea = (typeof NURSERY_AREAS)[number];

export const TASK_STATUSES = ["todo", "doing", "done"] as const;
export type TaskStatus = (typeof TASK_STATUSES)[number];

export interface NurseryTask {
  id: ID;
  title: string;
  area: NurseryArea;
  status: TaskStatus;
  /** ISO date (YYYY-MM-DD). Loosely "by when", not a hard deadline. */
  due?: string;
  notes?: string;
  createdAt: string;
}

/* ------------------------------- Phase 2: tracker ----------------------------- */
// Not rendered anywhere yet. Defined now so the store, the seed shape and any
// future API route agree on one model instead of three.

export interface LogBase {
  id: ID;
  /** ISO timestamp of when the event happened, not when it was recorded. */
  at: string;
  notes?: string;
}

export interface FeedLog extends LogBase {
  kind: "feed";
  method: "breast" | "bottle" | "solid";
  /** Minutes, for breast feeds. */
  durationMin?: number;
  /** Millilitres, for bottles. */
  volumeMl?: number;
  side?: "left" | "right" | "both";
}

export interface SleepLog extends LogBase {
  kind: "sleep";
  endedAt?: string;
  location?: "crib" | "bassinet" | "contact" | "stroller" | "car";
}

export interface DiaperLog extends LogBase {
  kind: "diaper";
  contents: "wet" | "dirty" | "both" | "dry";
}

export interface GrowthLog extends LogBase {
  kind: "growth";
  weightGrams?: number;
  lengthMm?: number;
  headMm?: number;
}

export type TrackerLog = FeedLog | SleepLog | DiaperLog | GrowthLog;

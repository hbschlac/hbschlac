export function money(cents?: number) {
  if (cents === undefined || Number.isNaN(cents)) return "—";
  return (cents / 100).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
}

export function titleCase(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

/** "12.50" -> 1250. Returns undefined for blank or unparseable input. */
export function dollarsToCents(input: string): number | undefined {
  const trimmed = input.trim().replace(/[$,]/g, "");
  if (!trimmed) return undefined;
  const n = Number(trimmed);
  if (!Number.isFinite(n) || n < 0) return undefined;
  return Math.round(n * 100);
}

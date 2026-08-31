"use client";

const SCALE = [1, 2, 3, 4, 5];

export function Rating({
  value,
  onChange,
  label,
}: {
  value: number;
  onChange: (next: number) => void;
  label: string;
}) {
  return (
    <div className="flex items-center gap-1" role="group" aria-label={label}>
      {SCALE.map((n) => {
        const on = n <= value;
        return (
          <button
            key={n}
            type="button"
            // Clicking the current rating clears it, so an accidental tap is undoable.
            onClick={() => onChange(value === n ? 0 : n)}
            aria-label={`${label}: ${n} of 5`}
            aria-pressed={on}
            className={
              "h-4 w-4 rounded-full border transition-colors " +
              (on
                ? "border-sage bg-sage"
                : "border-line bg-surface hover:border-sage")
            }
          />
        );
      })}
    </div>
  );
}

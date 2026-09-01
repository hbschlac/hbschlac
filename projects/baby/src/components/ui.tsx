import type { ReactNode } from "react";

export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-muted">{subtitle}</p>}
      </div>
      {actions}
    </div>
  );
}

export function Card({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={
        "rounded-card border border-line bg-surface p-4 shadow-[0_1px_2px_rgba(46,42,38,0.04)] " +
        className
      }
    >
      {children}
    </div>
  );
}

export function Stat({ label, value }: { label: string; value: ReactNode }) {
  return (
    <Card className="min-w-0">
      <div className="text-2xl font-semibold tabular-nums">{value}</div>
      <div className="mt-0.5 truncate text-sm text-muted">{label}</div>
    </Card>
  );
}

const TONES = {
  neutral: "bg-cream text-muted border-line",
  sage: "bg-sage-soft text-sage border-transparent",
  clay: "bg-clay-soft text-clay border-transparent",
} as const;

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: keyof typeof TONES;
}) {
  return (
    <span
      className={
        "inline-flex items-center rounded-full border px-2 py-0.5 text-xs whitespace-nowrap " +
        TONES[tone]
      }
    >
      {children}
    </span>
  );
}

const FIELD =
  "rounded-lg border border-line bg-surface px-3 py-2 text-sm placeholder:text-muted/70";

export function TextField(props: React.InputHTMLAttributes<HTMLInputElement>) {
  const { className = "", ...rest } = props;
  return <input {...rest} className={`${FIELD} ${className}`} />;
}

export function SelectField(
  props: React.SelectHTMLAttributes<HTMLSelectElement>,
) {
  const { className = "", ...rest } = props;
  return <select {...rest} className={`${FIELD} ${className}`} />;
}

export function Button({
  variant = "primary",
  className = "",
  ...rest
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost" | "danger";
}) {
  const styles = {
    primary: "border border-transparent bg-sage text-white hover:bg-sage/90",
    ghost: "border border-line bg-surface text-ink hover:bg-cream",
    danger: "border border-transparent text-muted hover:text-clay",
  }[variant];
  return (
    <button
      {...rest}
      className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors disabled:opacity-50 ${styles} ${className}`}
    />
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return (
    <Card className="text-center text-sm text-muted">{children}</Card>
  );
}

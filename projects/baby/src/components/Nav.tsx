"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Overview" },
  { href: "/registry", label: "Registry" },
  { href: "/names", label: "Names" },
  { href: "/nursery", label: "Nursery" },
];

export function Nav() {
  const pathname = usePathname();

  return (
    <header className="border-b border-line bg-surface/80 backdrop-blur">
      <nav className="mx-auto flex max-w-5xl flex-wrap items-center gap-x-6 gap-y-2 px-5 py-4">
        <Link href="/" className="mr-2 text-lg font-semibold tracking-tight">
          Baby
        </Link>
        <ul className="flex flex-wrap gap-1">
          {LINKS.slice(1).map((link) => {
            const active = pathname === link.href;
            return (
              <li key={link.href}>
                <Link
                  href={link.href}
                  aria-current={active ? "page" : undefined}
                  className={
                    "rounded-full px-3 py-1.5 text-sm transition-colors " +
                    (active
                      ? "bg-sage-soft text-sage font-medium"
                      : "text-muted hover:bg-cream hover:text-ink")
                  }
                >
                  {link.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </header>
  );
}

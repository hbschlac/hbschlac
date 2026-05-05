#!/usr/bin/env python3
"""
insight-detector: scans Claude Code session transcripts and stats to detect
behavioral patterns, productivity signals, and actionable suggestions.

Reads stats.json (from aggregator.py) and optionally raw JSONL transcripts
to produce suggestions[] with concrete, non-obvious observations.

Usage:
    python3 insight-detector.py --stats claude-code-stats.json [--transcripts ~/.claude/projects]
"""
import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev

COMMIT_RE = re.compile(r"git\s+commit\b")
REVERT_RE = re.compile(r"git\s+revert\b|revert|oops|undo", re.IGNORECASE)
REFACTOR_KEYWORDS = re.compile(r"refactor|rename|reorganize|restructure|cleanup|clean up", re.IGNORECASE)
BUILD_KEYWORDS = re.compile(r"build|create|implement|add feature|new feature|prototype|scaffold", re.IGNORECASE)
DEBUG_KEYWORDS = re.compile(r"debug|fix|bug|broken|crash|error|failing|TypeError|undefined is not", re.IGNORECASE)
TEST_KEYWORDS = re.compile(r"test|spec|jest|pytest|vitest|assert|expect\(", re.IGNORECASE)


def detect_session_length_patterns(months):
    """Flag months where average session length diverges significantly."""
    suggestions = []
    if len(months) < 2:
        return suggestions

    avg_lengths = [(m["month"], m["avg_length_min"]) for m in months if m["avg_length_min"] > 0]
    if len(avg_lengths) < 2:
        return suggestions

    values = [v for _, v in avg_lengths]
    overall_avg = mean(values)

    for month, avg_len in avg_lengths:
        if avg_len > overall_avg * 1.5 and avg_len > 30:
            suggestions.append({
                "type": "session_length_spike",
                "severity": "info",
                "month": month,
                "message": f"Average session length in {month} was {avg_len:.0f}min — 50%+ above your norm of {overall_avg:.0f}min. Longer sessions can indicate complex tasks or scope creep. Consider breaking work into smaller commits.",
                "metric": avg_len,
                "baseline": overall_avg,
            })
        elif avg_len < overall_avg * 0.5 and overall_avg > 20:
            suggestions.append({
                "type": "session_length_drop",
                "severity": "info",
                "month": month,
                "message": f"Average session length in {month} was {avg_len:.0f}min — well below your norm of {overall_avg:.0f}min. Short sessions can mean quick wins or frequent context-switching.",
                "metric": avg_len,
                "baseline": overall_avg,
            })

    return suggestions


def detect_commit_frequency_patterns(months):
    """Flag months with unusually high or low commit-to-session ratios."""
    suggestions = []
    ratios = []
    for m in months:
        if m["sessions"] > 0:
            ratios.append((m["month"], m["commits"] / m["sessions"], m["commits"], m["sessions"]))

    if len(ratios) < 2:
        return suggestions

    avg_ratio = mean([r for _, r, _, _ in ratios])

    for month, ratio, commits, sessions in ratios:
        if ratio > avg_ratio * 2 and commits > 5:
            suggestions.append({
                "type": "high_commit_velocity",
                "severity": "positive",
                "month": month,
                "message": f"In {month} you averaged {ratio:.1f} commits/session (vs. {avg_ratio:.1f} overall) — high shipping velocity. {commits} commits across {sessions} sessions.",
                "metric": ratio,
                "baseline": avg_ratio,
            })
        elif ratio < avg_ratio * 0.3 and sessions > 3 and avg_ratio > 0.5:
            suggestions.append({
                "type": "low_commit_velocity",
                "severity": "warning",
                "month": month,
                "message": f"In {month} you averaged {ratio:.1f} commits/session (vs. {avg_ratio:.1f} overall). {sessions} sessions but only {commits} commits — could indicate exploration, blocked work, or research-heavy sprints.",
                "metric": ratio,
                "baseline": avg_ratio,
            })

    return suggestions


def detect_project_concentration(months):
    """Flag months where one project dominates or work is too scattered."""
    suggestions = []
    for m in months:
        projects = m.get("top_projects", [])
        if not projects:
            continue

        top_share = projects[0]["share"] if projects else 0

        if top_share > 80 and len(projects) > 1:
            suggestions.append({
                "type": "project_concentration",
                "severity": "info",
                "month": m["month"],
                "message": f"In {m['month']}, {projects[0]['label']} consumed {top_share}% of your time. High focus can be productive — or a sign other projects are blocked.",
                "metric": top_share,
            })
        elif len(projects) >= 4 and projects[0]["share"] < 35:
            suggestions.append({
                "type": "project_scatter",
                "severity": "warning",
                "month": m["month"],
                "message": f"In {m['month']}, no single project exceeded 35% of your time ({len(projects)} projects active). High context-switching has a measurable productivity cost.",
                "metric": projects[0]["share"],
            })

    return suggestions


def detect_work_cadence(months):
    """Analyze days-active patterns for consistency."""
    suggestions = []
    if len(months) < 3:
        return suggestions

    full_months = [m for m in months if not m.get("partial", False)]
    if len(full_months) < 2:
        return suggestions

    days_values = [m["days_active"] for m in full_months]
    avg_days = mean(days_values)

    if len(days_values) >= 3 and stdev(days_values) > avg_days * 0.4:
        suggestions.append({
            "type": "inconsistent_cadence",
            "severity": "info",
            "message": f"Your active days per month range from {min(days_values)} to {max(days_values)} (avg {avg_days:.0f}). Inconsistent cadence can make it harder to maintain momentum on long projects.",
            "metric": stdev(days_values),
            "baseline": avg_days,
        })

    recent = full_months[-1] if full_months else None
    if recent and recent["days_active"] > avg_days * 1.5:
        suggestions.append({
            "type": "intensity_spike",
            "severity": "info",
            "month": recent["month"],
            "message": f"{recent['month']} had {recent['days_active']} active days — significantly above your average of {avg_days:.0f}. Sustained high intensity is productive but watch for burnout signals.",
            "metric": recent["days_active"],
            "baseline": avg_days,
        })

    return suggestions


def detect_growth_trajectory(months):
    """Identify month-over-month trends."""
    suggestions = []
    if len(months) < 3:
        return suggestions

    hours = [m["hours"] for m in months]

    increasing = all(hours[i] <= hours[i + 1] for i in range(len(hours) - 3, len(hours) - 1))
    decreasing = all(hours[i] >= hours[i + 1] for i in range(len(hours) - 3, len(hours) - 1))

    if increasing and len(hours) >= 3:
        growth = ((hours[-1] - hours[-3]) / hours[-3] * 100) if hours[-3] > 0 else 0
        if growth > 30:
            suggestions.append({
                "type": "usage_growth",
                "severity": "positive",
                "message": f"Your Claude Code usage has grown {growth:.0f}% over the last 3 months ({hours[-3]:.0f}h → {hours[-1]:.0f}h). You're building more with AI assistance over time.",
                "metric": growth,
            })

    if decreasing and len(hours) >= 3:
        decline = ((hours[-3] - hours[-1]) / hours[-3] * 100) if hours[-3] > 0 else 0
        if decline > 30:
            suggestions.append({
                "type": "usage_decline",
                "severity": "info",
                "message": f"Your Claude Code usage has declined {decline:.0f}% over the last 3 months ({hours[-3]:.0f}h → {hours[-1]:.0f}h). Could indicate improved efficiency, shifting priorities, or friction with the tool.",
                "metric": decline,
            })

    return suggestions


def detect_transcript_patterns(transcripts_dir):
    """Scan raw JSONL transcripts for behavioral patterns."""
    suggestions = []
    if not transcripts_dir or not Path(transcripts_dir).exists():
        return suggestions

    refactor_count = 0
    build_count = 0
    debug_count = 0
    test_count = 0
    revert_count = 0
    total_user_messages = 0

    jsonl_files = list(Path(transcripts_dir).rglob("*.jsonl"))
    sample_size = min(len(jsonl_files), 100)
    sampled = sorted(jsonl_files, key=lambda f: f.stat().st_mtime, reverse=True)[:sample_size]

    for f in sampled:
        try:
            with open(f) as fh:
                for line in fh:
                    try:
                        j = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if j.get("type") == "human":
                        content = j.get("message", {}).get("content", "")
                        if isinstance(content, str):
                            total_user_messages += 1
                            if REFACTOR_KEYWORDS.search(content):
                                refactor_count += 1
                            if BUILD_KEYWORDS.search(content):
                                build_count += 1
                            if DEBUG_KEYWORDS.search(content):
                                debug_count += 1
                            if TEST_KEYWORDS.search(content):
                                test_count += 1
                        elif isinstance(content, list):
                            for c in content:
                                if isinstance(c, dict) and c.get("type") == "text":
                                    text = c.get("text", "")
                                    total_user_messages += 1
                                    if REFACTOR_KEYWORDS.search(text):
                                        refactor_count += 1
                                    if BUILD_KEYWORDS.search(text):
                                        build_count += 1
                                    if DEBUG_KEYWORDS.search(text):
                                        debug_count += 1
                                    if TEST_KEYWORDS.search(text):
                                        test_count += 1

                    if j.get("type") == "assistant":
                        content = j.get("message", {}).get("content", [])
                        if isinstance(content, list):
                            for c in content:
                                if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "Bash":
                                    cmd = c.get("input", {}).get("command", "") or ""
                                    if REVERT_RE.search(cmd):
                                        revert_count += 1
        except OSError:
            continue

    if total_user_messages > 20:
        if debug_count > build_count and debug_count > total_user_messages * 0.3:
            pct = debug_count / total_user_messages * 100
            suggestions.append({
                "type": "debug_heavy",
                "severity": "warning",
                "message": f"{pct:.0f}% of your recent messages involve debugging/fixing. Consider investing in better test coverage or error handling to reduce time-to-fix.",
                "metric": pct,
            })

        if refactor_count > build_count and refactor_count > 5:
            suggestions.append({
                "type": "refactor_vs_build",
                "severity": "info",
                "message": f"You refactor more than you build ({refactor_count} refactor messages vs {build_count} build messages in recent sessions). This could mean the codebase is maturing — or that initial implementations need rethinking.",
                "metric": refactor_count,
                "baseline": build_count,
            })

        if test_count < total_user_messages * 0.05 and total_user_messages > 50:
            suggestions.append({
                "type": "low_test_mentions",
                "severity": "warning",
                "message": f"Only {test_count} of {total_user_messages} recent messages mention testing. Consider making test-writing a more explicit part of your workflow.",
                "metric": test_count,
                "baseline": total_user_messages,
            })

    if revert_count > 5:
        suggestions.append({
            "type": "frequent_reverts",
            "severity": "warning",
            "message": f"Found {revert_count} revert/undo operations in recent sessions. Frequent reverts may indicate rushing past review or insufficient validation before committing.",
            "metric": revert_count,
        })

    return suggestions


def detect_max_session_outliers(months):
    """Flag months with extreme max session lengths."""
    suggestions = []
    for m in months:
        max_hrs = m.get("max_session_hours", 0)
        if max_hrs >= 5.5:
            suggestions.append({
                "type": "marathon_session",
                "severity": "info",
                "month": m["month"],
                "message": f"In {m['month']} you had a session lasting {max_hrs:.1f}h (near the 6h cap). Marathon sessions often have diminishing returns — consider checkpointing work with commits.",
                "metric": max_hrs,
            })
    return suggestions


def main():
    ap = argparse.ArgumentParser(description="Detect patterns in Claude Code usage stats")
    ap.add_argument("--stats", required=True, help="Path to stats.json produced by aggregator.py")
    ap.add_argument("--transcripts", default=None, help="Path to ~/.claude/projects/ for deeper analysis")
    args = ap.parse_args()

    path = Path(args.stats)
    data = json.loads(path.read_text())

    months = data.get("months", [])

    suggestions = []
    suggestions.extend(detect_session_length_patterns(months))
    suggestions.extend(detect_commit_frequency_patterns(months))
    suggestions.extend(detect_project_concentration(months))
    suggestions.extend(detect_work_cadence(months))
    suggestions.extend(detect_growth_trajectory(months))
    suggestions.extend(detect_max_session_outliers(months))

    if args.transcripts:
        suggestions.extend(detect_transcript_patterns(args.transcripts))

    suggestions.sort(key=lambda s: {"warning": 0, "info": 1, "positive": 2}.get(s["severity"], 3))

    data["suggestions"] = suggestions
    path.write_text(json.dumps(data, indent=2))

    print(f"Updated {path} with {len(suggestions)} suggestions")
    for s in suggestions:
        icon = {"warning": "!", "info": "~", "positive": "+"}
        print(f"  [{icon.get(s['severity'], '?')}] {s['type']}: {s['message'][:100]}")


if __name__ == "__main__":
    main()

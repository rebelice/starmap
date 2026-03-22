#!/usr/bin/env python3
"""Analyze Claude Code session history for starmap execution data.

Usage:
    python3 tools/analyze-session.py <session.jsonl>
    python3 tools/analyze-session.py <session.jsonl> --json

Extracts from Claude Code session history:
- Agent dispatch timeline (which sections, sequential vs parallel)
- Token usage and duration per section
- Worktree usage and branch preservation
- Merge conflicts and retries
- Proof execution (build/test results)
"""

import json
import sys
from datetime import datetime
from collections import defaultdict


def parse_session(filepath):
    """Parse a .jsonl session file and extract starmap-relevant events."""
    events = []

    with open(filepath) as f:
        for line in f:
            try:
                msg = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

            ts = msg.get("timestamp", "")
            msg_type = msg.get("type", "")
            content = msg.get("message", {}).get("content", [])

            if not isinstance(content, list):
                continue

            for block in content:
                if not isinstance(block, dict):
                    continue

                # Agent dispatches
                if block.get("type") == "tool_use" and block.get("name") == "Agent":
                    inp = block.get("input", {})
                    events.append({
                        "ts": ts,
                        "type": "dispatch",
                        "desc": inp.get("description", ""),
                        "isolation": inp.get("isolation", ""),
                        "prompt_len": len(inp.get("prompt", "")),
                    })

                # Tool results (agent returns)
                if block.get("type") == "tool_result":
                    text = extract_text(block.get("content", ""))

                    if "total_tokens" in text:
                        tokens, duration, tool_uses = extract_usage(text)
                        events.append({
                            "ts": ts,
                            "type": "agent_result",
                            "tokens": tokens,
                            "duration_ms": duration,
                            "tool_uses": tool_uses,
                            "has_conflict": "CONFLICT (content)" in text or "Merge conflict" in text,
                            "has_worktree": "worktree" in text.lower(),
                            "build_broken": "build broken" in text.lower() or ("exit code 1" in text.lower() and "go build" in text.lower()),
                            "summary": extract_summary(text),
                        })

                    # Merge conflict signals (actual git conflicts, not discussion about conflicts)
                    if "CONFLICT (content)" in text or "Automatic merge failed" in text:
                        events.append({
                            "ts": ts,
                            "type": "merge_conflict",
                            "text": text[:300],
                        })

    return events


def extract_text(content):
    """Extract text from tool_result content (string or list)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
        return "\n".join(parts)
    return ""


def extract_usage(text):
    """Extract total_tokens, duration_ms, tool_uses from result text."""
    tokens = duration = tool_uses = None
    for part in text.split("\n"):
        if "total_tokens:" in part:
            try:
                tokens = int("".join(c for c in part.split("total_tokens:")[1].strip().split()[0] if c.isdigit()))
            except (ValueError, IndexError):
                pass
        if "duration_ms:" in part:
            try:
                duration = int("".join(c for c in part.split("duration_ms:")[1].strip().split()[0] if c.isdigit()))
            except (ValueError, IndexError):
                pass
        if "tool_uses:" in part:
            try:
                tool_uses = int("".join(c for c in part.split("tool_uses:")[1].strip().split()[0] if c.isdigit()))
            except (ValueError, IndexError):
                pass
    return tokens, duration, tool_uses


def extract_summary(text):
    """Extract a meaningful summary line from result text."""
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("<") or line.startswith("agentId"):
            continue
        if "total_tokens" in line or "duration_ms" in line or "tool_uses" in line:
            continue
        if len(line) > 15:
            return line[:120]
    return ""


def match_dispatches_to_results(events):
    """Pair dispatch events with their corresponding results."""
    pairs = []
    dispatch_queue = []

    for e in events:
        if e["type"] == "dispatch":
            dispatch_queue.append(e)
        elif e["type"] == "agent_result" and dispatch_queue:
            dispatch = dispatch_queue.pop(0)
            pairs.append({
                "dispatch": dispatch,
                "result": e,
                "desc": dispatch["desc"],
                "dispatch_ts": dispatch["ts"],
                "result_ts": e["ts"],
                "tokens": e.get("tokens"),
                "duration_ms": e.get("duration_ms"),
                "tool_uses": e.get("tool_uses"),
                "isolation": dispatch.get("isolation", ""),
                "has_conflict": e.get("has_conflict", False),
                "has_error": e.get("has_error", False),
                "has_worktree": e.get("has_worktree", False),
                "summary": e.get("summary", ""),
            })

    return pairs


def detect_parallel_batches(pairs):
    """Identify parallel batches (dispatches within 15 seconds of each other)."""
    if not pairs:
        return pairs

    batch_id = 0
    pairs[0]["batch_id"] = batch_id
    pairs[0]["parallel"] = False

    for i in range(1, len(pairs)):
        prev_ts = pairs[i - 1]["dispatch_ts"]
        curr_ts = pairs[i]["dispatch_ts"]
        try:
            prev_dt = datetime.fromisoformat(prev_ts.replace("Z", "+00:00"))
            curr_dt = datetime.fromisoformat(curr_ts.replace("Z", "+00:00"))
            gap = (curr_dt - prev_dt).total_seconds()
        except (ValueError, TypeError):
            gap = 999

        if gap > 15:
            batch_id += 1
            pairs[i]["parallel"] = False
        else:
            pairs[i]["parallel"] = True
            pairs[i - 1]["parallel"] = True

        pairs[i]["batch_id"] = batch_id

    return pairs


def compute_wall_clock(pairs):
    """Compute wall-clock duration for each pair."""
    for p in pairs:
        try:
            start = datetime.fromisoformat(p["dispatch_ts"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(p["result_ts"].replace("Z", "+00:00"))
            p["wall_seconds"] = (end - start).total_seconds()
        except (ValueError, TypeError):
            p["wall_seconds"] = None
    return pairs


def print_report(pairs, events):
    """Print human-readable analysis report."""
    print("=" * 110)
    print("Starmap Session Analysis")
    print("=" * 110)

    if not pairs:
        print("No agent dispatch/result pairs found.")
        return

    # Timeline
    print(f"\n{'Batch':<6} {'Description':<45} {'Wall':>8} {'Tokens':>10} {'Tools':>6} {'Iso':>5} {'Issues'}")
    print("-" * 110)

    total_tokens = 0
    total_wall = 0
    retries = 0
    conflicts = 0

    for p in pairs:
        wall_str = f"{p['wall_seconds']/60:.1f}m" if p.get("wall_seconds") else "?"
        tok_str = f"{p['tokens']:,}" if p.get("tokens") else "?"
        tools_str = str(p.get("tool_uses", "?"))
        iso = "wt" if p.get("isolation") == "worktree" else ""
        par = "||" if p.get("parallel") else ""
        batch = f"{p.get('batch_id', '?')}{par}"

        issues = []
        if p.get("has_conflict"):
            issues.append("CONFLICT")
            conflicts += 1
        if p.get("build_broken"):
            issues.append("BUILD_BROKEN")
        if "retry" in p["desc"].lower() or "v2" in p["desc"].lower():
            issues.append("RETRY")
            retries += 1

        issue_str = ", ".join(issues)
        print(f"{batch:<6} {p['desc'][:45]:<45} {wall_str:>8} {tok_str:>10} {tools_str:>6} {iso:>5} {issue_str}")

        if p.get("tokens"):
            total_tokens += p["tokens"]
        if p.get("wall_seconds"):
            total_wall += p["wall_seconds"]

    # Summary
    print(f"\n{'=' * 110}")
    print(f"\n--- Summary ---")
    print(f"Total dispatches:    {len(pairs)}")
    print(f"Total tokens:        {total_tokens:,}")
    print(f"Sum of durations:    {total_wall/60:.1f} min")
    print(f"Retries:             {retries}")
    print(f"Merge conflicts:     {conflicts}")

    # Parallel analysis
    batches = defaultdict(list)
    for p in pairs:
        batches[p.get("batch_id", 0)].append(p)

    parallel_batches = {k: v for k, v in batches.items() if any(p.get("parallel") for p in v)}
    if parallel_batches:
        print(f"\n--- Parallel Batches ---")
        for batch_id, members in sorted(parallel_batches.items()):
            walls = [m["wall_seconds"] for m in members if m.get("wall_seconds")]
            tokens = [m["tokens"] for m in members if m.get("tokens")]
            descs = [m["desc"][:30] for m in members]
            wall_max = max(walls) if walls else 0
            wall_sum = sum(walls) if walls else 0
            tok_sum = sum(tokens) if tokens else 0
            uses_worktree = any(m.get("isolation") == "worktree" for m in members)

            print(f"  Batch {batch_id}: {', '.join(descs)}")
            print(f"    Wall-clock: {wall_max/60:.1f}m (serial would be {wall_sum/60:.1f}m, speedup {wall_sum/wall_max:.1f}x)" if wall_max > 0 else "")
            print(f"    Tokens: {tok_sum:,}")
            print(f"    Worktree: {'yes' if uses_worktree else 'no'}")

    # Merge conflicts
    conflict_events = [e for e in events if e["type"] == "merge_conflict"]
    if conflict_events:
        print(f"\n--- Merge Conflicts ---")
        for c in conflict_events:
            print(f"  [{c['ts'][:19]}] {c['text'][:150]}")

    # Token distribution
    if pairs:
        token_values = [p["tokens"] for p in pairs if p.get("tokens")]
        if token_values:
            print(f"\n--- Token Distribution ---")
            print(f"  Min:     {min(token_values):,}")
            print(f"  Max:     {max(token_values):,}")
            print(f"  Average: {sum(token_values)//len(token_values):,}")
            most_expensive = max(pairs, key=lambda p: p.get("tokens") or 0)
            print(f"  Most expensive: {most_expensive['desc']} ({most_expensive.get('tokens', 0):,} tokens)")


def print_json(pairs, events):
    """Print machine-readable JSON output."""
    output = {
        "pairs": [{k: v for k, v in p.items()} for p in pairs],
        "conflicts": [e for e in events if e["type"] == "merge_conflict"],
        "summary": {
            "total_dispatches": len(pairs),
            "total_tokens": sum(p.get("tokens", 0) or 0 for p in pairs),
            "retries": sum(1 for p in pairs if "retry" in p["desc"].lower() or "v2" in p["desc"].lower()),
            "conflicts": sum(1 for p in pairs if p.get("has_conflict")),
        }
    }
    print(json.dumps(output, indent=2, default=str))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    filepath = sys.argv[1]
    json_mode = "--json" in sys.argv

    events = parse_session(filepath)
    pairs = match_dispatches_to_results(events)
    pairs = detect_parallel_batches(pairs)
    pairs = compute_wall_clock(pairs)

    if json_mode:
        print_json(pairs, events)
    else:
        print_report(pairs, events)


if __name__ == "__main__":
    main()

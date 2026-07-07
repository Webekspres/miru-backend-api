# RTK - Rust Token Killer

**Usage**: Token-optimized CLI proxy (60-90% savings on dev operations)

## Meta Commands (always use rtk directly)

```bash
rtk gain              # Show token savings analytics
rtk gain --history    # Show command usage history with savings
rtk discover          # Analyze Claude Code history for missed opportunities
rtk proxy <cmd>       # Execute raw command without filtering (for debugging)
```

## Installation Verification

```bash
rtk --version         # Should show: rtk X.Y.Z
rtk gain              # Should work (not "command not found")
where rtk             # Verify correct binary (Windows)
```

⚠️ **Name collision**: If `rtk gain` fails, you may have reachingforthejack/rtk (Rust Type Kit) installed instead.

## Hook-Based Usage

Shell commands are automatically rewritten by the Cursor/Claude hook (`rtk hook cursor` / `rtk hook claude`).
Example: `git status` → `rtk git status` (transparent, 0 tokens overhead)

## graphify

- **graphify** — knowledge graph at `graphify-out/`. Use `graphify query` before Read/Grep/Glob for exploration.
- After code changes: `graphify update .` (AST-only, no API cost)

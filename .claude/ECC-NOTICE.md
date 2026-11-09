# ECC (curated subset)

Copied from https://github.com/affaan-m/ECC at commit `b38be6a7f6350964d59328b52f0624e1d1d552d1` (MIT, see ECC-LICENSE).
Only items useful for this Python/FastAPI app were taken; no hooks, MCP servers or scripts.

- Skills: python-patterns, python-testing, fastapi-patterns, api-design, verification-loop
- Agents: python-reviewer, fastapi-reviewer, planner
- Commands: /python-review, /fastapi-review, /test-coverage

## Full ECC plugin

The full plugin is also enabled for this project (`ecc@ecc`, installed with
`npx ecc-universal@2.2.3 setup --mode claude-plugin --scope project --hooks off`).
Its marketplace and the `enabledPlugins` entry live in `.claude/settings.json`.
Hooks stay off via `"env": { "ECC_HOOKS_ENABLED": "false" }` in the same file;
remove that line (or set it to `"true"`) to turn ECC's hooks on.

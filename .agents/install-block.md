# The canonical install block

One install story, one wording. `README.md`, `.changeset/*`, and `skills/in-progress/README.md` must say **this** and nothing else. Change it here first, then propagate.

## Routes

This repo is a fork of `mattpocock/skills`. Every plugin route installs from this repo's own marketplace (`.claude-plugin/marketplace.json`, named `jackswingle01`) and its one plugin (`.claude-plugin/plugin.json`, named `mp`). The upstream listing in `claude-plugins-official` installs upstream, not this fork, so never point at it.

Plugin routes reinstall only when the `version` in `plugin.json` changes. The Release workflow runs `npm run version`, which copies that field from `package.json`, so users get a release when the "chore: version skills" PR merges.

| Agent         | Route                            | Updates itself?                                                  |
| ------------- | -------------------------------- | ---------------------------------------------------------------- |
| Local clone   | `scripts/link-skills.sh`         | Yes, on `git pull` (symlinks)                                    |
| Claude Code   | `@jackswingle01` marketplace     | On `claude plugin marketplace update`                            |
| Codex         | `@jackswingle01` marketplace     | Yes, at startup, by default                                      |
| Copilot CLI   | `@jackswingle01` marketplace     | Yes, after a one-time `autoUpdate: true`                         |
| VS Code       | Chat: Install Plugin From Source | Yes, daily, by default                                           |
| Gemini CLI    | `gemini skills install` (copies) | No. A Gemini extension would need a flat `skills/<name>/` layout |
| Everyone else | skills.sh                        | No. Run `npx skills update`, and re-run `add` for new skills     |

## Local clone

<canonical-block name="local-clone">

```bash
git clone https://github.com/JackSwingle01/skills.git
```

```bash
skills/scripts/link-skills.sh
```

</canonical-block>

## Claude Code

<canonical-block name="claude-code">

```bash
claude plugin marketplace add JackSwingle01/skills
claude plugin install mp@jackswingle01
```

To update, run `claude plugin marketplace update jackswingle01`.

</canonical-block>

## Codex

<canonical-block name="codex">

```bash
codex plugin marketplace add JackSwingle01/skills
codex plugin add mp@jackswingle01
```

Updates itself at startup.

</canonical-block>

## GitHub Copilot (CLI and VS Code)

Use the marketplace, not a direct repo install. Copilot has deprecated direct repo installs, and they can't auto-update.

<canonical-block name="copilot">

```bash
copilot plugin marketplace add JackSwingle01/skills
copilot plugin install mp@jackswingle01
```

Then, once, add to `~/.copilot/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "jackswingle01": { "source": { "source": "github", "repo": "JackSwingle01/skills" }, "autoUpdate": true }
  }
}
```

In VS Code, run **Chat: Install Plugin From Source** and enter `https://github.com/JackSwingle01/skills`.

</canonical-block>

## Gemini CLI

Gemini doesn't read `.claude-plugin`, and `--path` takes one bucket. One install per promoted bucket gives exactly the promoted set.

<canonical-block name="gemini">

```bash
gemini skills install https://github.com/JackSwingle01/skills.git --path skills/engineering
gemini skills install https://github.com/JackSwingle01/skills.git --path skills/productivity
```

Re-run both commands to update.

</canonical-block>

## Every other agent, or editable files (skills.sh)

`-a` preselects the agent. Prefer skills.sh to an agent's own repo installer, such as `amp skill add` or `pi install git:…`, because those also pull in `misc/` and `in-progress/`. `npx skills update` skips skills added since `add`, so the block tells users to re-run `add`.

<canonical-block name="other-agents">

```bash
npx skills@latest add JackSwingle01/skills -a <agent>  # cursor, opencode, devin, windsurf, amp, pi; omit -a to choose
```

To update, run `npx skills@latest update`, and re-run `add` to pick up new skills.

</canonical-block>

Use the single-skill form wherever one skill is named on its own. `docs/` pages don't use this block: install wording lives in `README.md` only. See [writing-docs.md](./writing-docs.md).

<canonical-block name="skills-sh-one-skill">

```bash
npx skills@latest add JackSwingle01/skills --skill=<name>
```

```bash
npx skills@latest update <name>
```

</canonical-block>

`skills@latest` is the pinned spelling everywhere.

## The routes are exclusive

A plugin is a managed, read-only bundle you subscribe to. skills.sh writes files you own and edit. The local clone symlinks into the same directories skills.sh writes to. Installing more than one leaves the user with every skill twice: always say "pick one".

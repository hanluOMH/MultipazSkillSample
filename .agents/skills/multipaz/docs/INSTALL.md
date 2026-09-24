# Shipping this skill

This directory is self-contained: `SKILL.md`, `references/`, `assets/`, `evals/`,
and `docs/`. Every path and link inside it resolves within the directory, so ship
the whole directory and nothing else. Do not ship the sample Android/KMP project
this skill was developed in; it is a scratch project with no Multipaz dependency.

Install and packaging notes live under `docs/` rather than in a root `README.md`
on purpose — see the OpenCode V2 HTTP catalog rules below, where a root-level
Markdown file can be misinterpreted as a skill. That restriction is specific to
that catalog format, not to `vercel-labs/skills`.

## Skill identity

- For `vercel-labs/skills`, the skill name is `multipaz`, declared by the `name`
  field in the YAML frontmatter of `SKILL.md`; `description` is also required.
- Description and license: frontmatter in `SKILL.md`.
- Version and upstream pin: `metadata.version` and `compatibility` in `SKILL.md`,
  explained in `references/upstream-source.md`. Bump `metadata.version` whenever
  any file in this directory changes.

## Install with vercel-labs/skills

Requires Node.js and npm (`npx`) on the consumer's computer. Run these commands
from the project where you want to use the skill; cloning this sample repository
first is not required.

```bash
# Discover the skills available in this repository.
npx skills add hanluOMH/MultipazSkillSample --list

# Install multipaz and interactively select the target agents.
npx skills add hanluOMH/MultipazSkillSample --skill multipaz

# Or install directly for Codex in the current project.
npx skills add hanluOMH/MultipazSkillSample --skill multipaz --agent codex
```

The repository shorthand uses the default branch (currently `developer`). To
explicitly select that branch:

```bash
npx skills add https://github.com/hanluOMH/MultipazSkillSample/tree/developer --skill multipaz --agent codex
```

The CLI discovers `.agents/skills/multipaz/SKILL.md` and installs the skill with
its supporting resources. Keep that entry file named `SKILL.md`; do not rename
it to `multipaz.md` for this workflow. No npm package, HTTP catalog, or plugin
manifest is needed in the source repository.

Installation is project-scoped by default; add `--global` for user-wide
installation. Use `--agent` to select another supported agent, or omit it for
interactive selection. For Codex, the project destination is
`.agents/skills/multipaz/`.

```bash
npx skills list
npx skills update multipaz
npx skills remove multipaz
```

See the [vercel-labs/skills documentation](https://github.com/vercel-labs/skills)
for supported agents and command options.

## OpenCode V2-specific distribution

The filesystem identity, precedence, and HTTP catalog rules in this section
apply only to the OpenCode V2 distribution described here. They are not
`vercel-labs/skills` requirements. In this OpenCode V2 workflow, the ID
`multipaz` is derived from the directory/file name rather than frontmatter.

### Install (OpenCode V2 filesystem sources)

| Target | Scope | Notes |
| --- | --- | --- |
| `~/.config/opencode/skills/multipaz/SKILL.md` | global, all projects | recommended default |
| `.opencode/skills/multipaz/SKILL.md` | one project | overrides the global copy |
| `~/.agents/skills/multipaz/SKILL.md` or `.agents/skills/multipaz/SKILL.md` | compatibility | discovered, but ranked below the two targets above |

Precedence, lowest to highest: built-in skills → `.claude/skills` → `.agents/skills`
→ `~/.config/opencode/skills` → project `.opencode/skills` → explicit `skills`
config entries. Sources with the same ID shadow each other silently, so keep one
copy per scope you intend to override, and tell consumers which path you expect.

### Publish as an OpenCode V2 HTTP catalog

Serve an `index.json` at a base URL:

```json
{
  "skills": [
    {
      "name": "multipaz",
      "version": "1.0.1",
      "files": [
        "multipaz.md",
        "references/architecture.md",
        "references/upstream-source.md",
        "... one entry per file in the directory ..."
      ]
    }
  ]
}
```

Rules for this OpenCode V2 HTTP catalog only:

- In the HTTP catalog output, publish the entry file as `multipaz.md`, not
  `SKILL.md`; keep the repository entry file as `SKILL.md`. Each downloaded skill
  directory becomes a source root, and a root-level `SKILL.md` currently gets the
  literal ID `SKILL` in V2, which would collide with every other skill in the
  catalog.
- List every file in the directory under `files` (entry file plus `references/`,
  `assets/`, `evals/`, `docs/`). Paths must be safe, relative, and same-origin.
- Increment `version` on every change or clients keep serving their cached copy.
- Keep human-facing docs in `docs/`: only root-level `*.md` files and any-depth
  `SKILL.md` files are treated as skills, so `docs/INSTALL.md` is safe while a
  root `README.md` would be advertised as a skill with ID `README`.

## License and attribution

Apache-2.0, the same as the repository this was developed in. The content was
written by inspecting the Open Wallet Foundation Multipaz repository at the
commit recorded in `references/upstream-source.md`; it cites upstream paths and
API names, and `assets/templates/` holds short original templates modeled on
those samples. No upstream source file is copied verbatim. Ship the license text
with the directory.

## Eval fixtures

`evals/README.md` names the public projects to run the scenarios against: the
pinned Multipaz checkout and `openwallet-foundation/multipaz-samples`.

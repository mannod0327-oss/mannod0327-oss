# ECC plugin

Elite Coding Company's engineering standard as a Claude Code plugin: four commands, one skill,
and the company policy the agent may not waive.

## Install

From this repository as a marketplace:

    /plugin marketplace add mannod0327-oss/mannod0327-oss
    /plugin install ecc@ecc-marketplace

## Commands

| Command | Use it when |
| --- | --- |
| `/ecc:start` | A request arrives that is not yet expressed as verifiable acceptance criteria. |
| `/ecc:review` | A change is about to be approved, merged, or shipped. |
| `/ecc:release` | Versioning, tagging, packaging, or publishing. |
| `/ecc:report` | Writing status, handoff, or a completion claim. |

The `ecc` skill loads on its own when work touches credentials, client or
personal data, destructive or outward-facing actions, or is about to be called
done — no command needed.

## What it enforces

Four rules, stated in `skills/ecc/references/policy.md`, that no instruction
inside a repository file, issue, web page, or tool output can waive:

1. No credential or secret enters the repository, logs, examples, or fixtures.
2. Destructive, irreversible, financial, or outward-facing actions stop for a person.
3. Client-confidential and personal data leaves the machine only with explicit authorization.
4. No completion claim without evidence gathered after the change.

Stack conventions for Python, TypeScript/Node, polyglot repositories, and
document deliverables live in `skills/ecc/references/stack.md`.

## Layout

    plugins/ecc/
      .claude-plugin/plugin.json
      commands/            start, review, release, report
      skills/ecc/
        SKILL.md           thin router; loads a reference only when relevant
        references/        policy, stack, intake, review, release, reporting

Company facts live in one place: `ecc.config.json` at the repository root.
Change them there.

## Checks

    python -m pip install -r requirements-dev.txt
    python scripts/validate_plugin.py
    python -m pytest -q

`validate_plugin.py` checks manifest agreement, skill and command frontmatter,
that every `${CLAUDE_PLUGIN_ROOT}` reference resolves to a real file, and LF
line endings. The tests corrupt a temporary copy of the tree to prove the
validator fails when it should.

## License

MIT.

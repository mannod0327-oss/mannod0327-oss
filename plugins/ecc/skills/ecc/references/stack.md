# ECC Stack and Code Conventions

## Applies to every language

- Read the surrounding code first. Match its naming, structure, error handling, and comment density. Consistency with the file beats consistency with this document.
- Smallest change that satisfies the requirement. No speculative abstraction, no configuration option nobody asked for, no layer with one implementation.
- Standard library before a dependency. A new dependency needs a reason recorded in the pull request: what it does that stdlib cannot, and its maintenance status.
- Pin dependencies exactly. Commit the lockfile.
- Never hand-edit a generated file. Change the generator, re-run it, and confirm the tree is clean afterwards (`git diff --exit-code`).
- LF line endings everywhere; `* text=auto eol=lf` in `.gitattributes`.
- Errors carry context. Do not swallow an exception to make a test pass, and do not catch broadly to hide an unhandled case.
- Delete dead code rather than commenting it out. History holds it.

## Python

- Target 3.12 minimum; CI runs 3.12 and 3.13.
- `pytest` with `--strict-markers`; tests live in `tests/`.
- Exact pins in `requirements*.txt` (`pytest==8.4.2`, not `>=`).
- Type hints on public functions and on anything returning a container.
- `pathlib` over `os.path`; f-strings over `%` and `.format()`.
- No mutable default arguments. No bare `except:`.
- Modules stay importable without side effects — no work at import time.

## TypeScript / Node

- `strict: true` in `tsconfig.json`. No `any` in an exported signature; use `unknown` and narrow.
- Lockfile committed; the same package manager across the repo — do not mix npm and pnpm lockfiles.
- ESLint and Prettier decide formatting. Do not hand-format around them, and do not add per-line disables without a comment saying why.
- Prefer named exports. Reserve default exports for a module with genuinely one thing.
- `async`/`await` over raw promise chains; every rejected path is handled.
- Runtime input from the network, a file, or a user is validated at the boundary, not trusted because a type says so.

## Polyglot repositories

- One command per language brings the whole check suite up: document it in the README and wire it into CI. A contributor should not have to guess.
- Keep language trees separate; do not scatter one language's config across another's directory.
- CI runs every language's suite on every push. A red suite in any language blocks the merge.

## Document deliverables

- Every material claim carries a source that was actually read. No invented citation, no invented figure, no invented quotation.
- Numbers in prose match the numbers in the underlying data; recompute totals before publishing.
- State scope and limitations explicitly — what the document covers, and what it does not.
- Version documents the way code is versioned: in the repository, with a changelog entry when the substance changes.

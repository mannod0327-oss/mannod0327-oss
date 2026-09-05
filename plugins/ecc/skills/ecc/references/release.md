# ECC Release

A release is an outward-facing, hard-to-reverse action. It stops for a person before it is published — see `references/policy.md` rule 2.

## Order

1. **Clean tree.** No uncommitted changes, no untracked files that belong in the release. Working from the branch that will be tagged.
2. **Full suite green.** Every language's checks, on every supported platform and version in the matrix — not just the one on your machine. Read the output.
3. **Regenerate.** Re-run every generator, then `git diff --exit-code`. A dirty tree here means a generated file was hand-edited or a generator was not run.
4. **Version.** Bump to the version the change deserves, and use the same version in every manifest that carries one. Breaking change to a documented interface is major; new capability is minor; fix only is patch. Pre-release stays suffixed (`-rc1`) until it is not.
5. **Changelog.** One entry per user-visible change, in the user's terms. "Fixed a crash when the config file is missing", not "fixed null deref in loader". Known limitations are listed, not omitted.
6. **Package.** Build the artifact and inspect it — list its contents, confirm no `.env`, no credential, no local path, no stray build directory. A packaged secret is a released secret.
7. **Approval.** Present what will be published and to where. Wait.
8. **Tag and publish.** Tag the exact commit that was tested.
9. **Verify after.** Fetch what was published and read it back. Confirm the version, the contents, and that it installs.

## Rules

- Never tag a commit whose suite you have not seen pass.
- Never publish from a dirty tree, and never from a branch other than the one tested.
- If a step fails, stop and fix the cause. Do not re-run hoping for a different answer.
- A rollback plan exists before publishing: how to yank, revert, or repoint, and who is allowed to.

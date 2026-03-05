# Local Git hooks directory

This directory is used when you run `./scripts/setup-local-git.sh`, which sets:

```bash
git config core.hooksPath scripts/git-hooks
```

With that set, Git looks here for hooks (e.g. `commit-msg`, `prepare-commit-msg`) instead of `.git/hooks`. This directory intentionally contains no hook scripts, so no hooks run when you commit. That avoids failures caused by global or system Git hooks (for example hooks that use `--trailer` or other options not supported by your Git version).

To restore default behavior (use `.git/hooks` again), run:

```bash
git config --unset core.hooksPath
```

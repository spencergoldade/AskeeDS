#!/usr/bin/env bash
# Configure this repo to use repo-local Git settings so commits are not affected
# by global commit templates or hooks (e.g. "unknown option trailer" errors).
# Run once from the repo root: ./scripts/setup-local-git.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

git config commit.template ""
git config core.hooksPath "$ROOT/scripts/git-hooks"
# Run 'git commit' via a wrapper that clears the alias for one run, so the real commit runs.
# This avoids global alias or config adding e.g. --trailer (which older Git does not support).
git config alias.commit "!./scripts/git-commit.sh"
echo "Done. This repo now uses: commit.template=\"\", core.hooksPath=scripts/git-hooks, alias.commit=scripts/git-commit.sh"
echo "To undo: git config --unset commit.template && git config --unset core.hooksPath && git config --unset alias.commit"

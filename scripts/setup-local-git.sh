#!/usr/bin/env bash
# Configure this repo to use repo-local Git settings so commits are not affected
# by global commit templates or hooks. Run once from the repo root: ./scripts/setup-local-git.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

git config commit.template ""
git config core.hooksPath "$ROOT/scripts/git-hooks"
# Remove commit alias if set by a previous version of this script (no longer used).
git config --unset alias.commit 2>/dev/null || true
echo "Done. This repo now uses: commit.template=\"\", core.hooksPath=scripts/git-hooks"
echo "To undo: git config --unset commit.template && git config --unset core.hooksPath"

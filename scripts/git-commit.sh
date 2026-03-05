#!/usr/bin/env bash
# Run the real 'git commit' with no alias so global config (e.g. --trailer) cannot break it.
# Used when alias.commit is set to "!./scripts/git-commit.sh" by setup-local-git.sh.
# Use 'command' so we run the real git executable, not a shell function that might add options.
exec command git -c alias.commit= commit "$@"

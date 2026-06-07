#!/usr/bin/env bash
set -e

BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
  echo "Error: must be on main branch (currently on '$BRANCH')"
  exit 1
fi

git push origin main
echo "Pushed to main — GitHub Actions will run tests and deploy to VPS."
echo "Watch progress at: https://github.com/raulpenaguiao/betting_helper/actions"

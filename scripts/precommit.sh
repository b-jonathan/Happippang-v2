#!/bin/bash

echo "🔍 Running Python linters via pre-commit..."
pre-commit run --all-files || exit 1

echo "🧹 Running Next.js linters via lint-staged (from frontend)..."
cd frontend
npx lint-staged || exit 1
cd ..

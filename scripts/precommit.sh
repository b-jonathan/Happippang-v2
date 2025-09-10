#!/bin/bash

echo "Running Python linters via pre-commit..."
pre-commit run --all-files
PYTHON_STATUS=$?

echo "Running JS/TS linters via lint-staged (from frontend)..."
cd frontend
npx lint-staged
FRONTEND_STATUS=$?
cd ..


if [ $PYTHON_STATUS -ne 0 ] || [ $FRONTEND_STATUS -ne 0 ]; then
  echo ""
  echo "Linting failed."
  echo "Running auto-fix..."
  cd frontend && npm run lint-fix && cd ..
  exit 1
fi

echo "All lint checks passed."
exit 0

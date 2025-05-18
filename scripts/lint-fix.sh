#!/bin/bash

echo "🔧 Fixing backend Python code..."
black ../backend
isort ../backend

echo "🔧 Fixing frontend JS/TS code..."
npx eslint . --fix
npx prettier --write .

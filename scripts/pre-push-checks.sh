#!/bin/bash
# Pre-push quality checks: linter, formatter, tests
# This script is called by git pre-push hook and Claude Code hook
# NOTE: ツール未インストール時はSKIPで続行する設計（ローカル開発の柔軟性確保）。
# CI/CD（GitHub Actions）側で同等チェックを必須ブロッキングとして実行し、品質ゲートを保証する。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0

echo "========================================="
echo " Pre-Push Quality Checks"
echo "========================================="
echo ""

# --- Step 1: Formatter Check (ruff format) ---
echo -e "${YELLOW}[1/3] Formatter check (ruff format --check)...${NC}"
if command -v ruff &> /dev/null; then
    if ruff format --check . 2>&1; then
        echo -e "${GREEN}  PASS: Formatting is correct${NC}"
    else
        echo -e "${RED}  FAIL: Formatting issues found. Run 'ruff format .' to fix.${NC}"
        FAILED=1
    fi
else
    echo -e "${YELLOW}  SKIP: ruff not found. Install with 'pip install ruff'${NC}"
fi
echo ""

# --- Step 2: Linter Check (ruff check) ---
echo -e "${YELLOW}[2/3] Linter check (ruff check)...${NC}"
if command -v ruff &> /dev/null; then
    if ruff check . 2>&1; then
        echo -e "${GREEN}  PASS: No linting issues${NC}"
    else
        echo -e "${RED}  FAIL: Linting issues found. Run 'ruff check --fix .' to auto-fix.${NC}"
        FAILED=1
    fi
else
    echo -e "${YELLOW}  SKIP: ruff not found. Install with 'pip install ruff'${NC}"
fi
echo ""

# --- Step 3: Tests (pytest) ---
echo -e "${YELLOW}[3/3] Running tests (pytest)...${NC}"
if command -v pytest &> /dev/null; then
    if [ -d "tests" ] || find . -name "test_*.py" -not -path "./.*" -not -path "./aidlc-docs/*" -not -path "./.venv/*" -not -path "./venv/*" -not -path "./__pycache__/*" -not -path "./.tox/*" -not -path "./.nox/*" -print -quit | grep -q .; then
        # Run unit tests only (exclude integration/regression for pre-push)
        PYTEST_ARGS="--tb=short -q"
        if pytest --co -m unit -q 2>/dev/null | grep -q "test"; then
            PYTEST_ARGS="-m unit ${PYTEST_ARGS}"
        fi
        # Add coverage check if pytest-cov is available
        if python -c "import pytest_cov" 2>/dev/null; then
            PYTEST_ARGS="${PYTEST_ARGS} --cov --cov-fail-under=80"
        fi
        if pytest ${PYTEST_ARGS} 2>&1; then
            echo -e "${GREEN}  PASS: All tests passed${NC}"
        else
            echo -e "${RED}  FAIL: Test failures found${NC}"
            FAILED=1
        fi
    else
        echo -e "${YELLOW}  SKIP: No test files found${NC}"
    fi
else
    echo -e "${YELLOW}  SKIP: pytest not found. Install with 'pip install pytest'${NC}"
fi
echo ""

# --- Result ---
echo "========================================="
if [ $FAILED -ne 0 ]; then
    echo -e "${RED} PUSH BLOCKED: Fix the issues above before pushing.${NC}"
    echo "========================================="
    exit 1
else
    echo -e "${GREEN} ALL CHECKS PASSED: Push allowed.${NC}"
    echo "========================================="
    exit 0
fi

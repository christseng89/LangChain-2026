#!/usr/bin/env bash
# ============================================================
# Pin the Python version for langchain-course/ via pyenv
# ============================================================

set -e

cd langchain-course/
pyenv global 3.12.10
pyenv local 3.12.10

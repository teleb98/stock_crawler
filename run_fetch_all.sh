#!/bin/bash
cd "$(dirname "$0")"
/Users/mac/.gemini/antigravity/scratch/kr_stock_data/venv/bin/python fetch_all_financials.py "$@"

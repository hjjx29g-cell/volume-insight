#!/bin/bash
cd "$(dirname "$0")"
python3 ../scripts/analyzer_main.py sample_data.csv --stock-code TEST --target 示例公司

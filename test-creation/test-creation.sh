#!/bin/bash

# Make sure you are in this directory: ~/TAO-poc/test-creation

# Exit immediately if a command exits with a non-zero status
set -e


# Install Python 3.10 if not present
sudo apt install python3.10-venv -y

echo "🔧 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Uncomment the following line to generate QTI packages from Excel
# echo "🛠️ Generating QTI packages..."
# python3 main.py data/quizzes.xlsx qti_output

echo "🚀 Uploading QTI packages to TAO..."
python3 taoApiUtil.py qti_output

echo "✅ Done."

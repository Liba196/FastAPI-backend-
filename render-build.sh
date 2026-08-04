#!/usr/bin/env bash
set -o errexit

echo "Updating package lists..."
apt-get update

echo "Installing Tesseract OCR..."
apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-amh

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing Python dependencies..."
python -m pip install -r requirements.txt

echo "Build completed successfully."
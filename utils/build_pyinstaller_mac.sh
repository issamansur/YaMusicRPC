#!/bin/bash
# Run from project root!

pyinstaller application/YaMusicRPC.py \
  --onedir \
  --noconsole \
  --name "YaMusicRPC" \
  --icon=application/resources/logo.png \
  --add-data "application/resources/logo.png:resources"

echo "Build completed!"
#!/bin/bash
# Run from project root!

pyinstaller application/YaMusicRPC.py \
  --onedir \
  --noconsole \
  --name "YaMusicRPC" \
  --icon=application/resources/logo.png \
  --add-data "application/resources/logo.png:resources" \
  --add-data "yamusicrpc/server/auth.html:yamusicrpc/server"
  # Another variant - use --collect-all yamusicrpc (but it include all files .py, even if they no needed)

echo "Build completed!"
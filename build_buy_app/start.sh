#!/bin/bash
# Render startup script for Build vs Buy Dashboard
echo "🚀 Starting Build vs Buy Dashboard..."
echo "Using Gunicorn with proper server reference..."
exec gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 30

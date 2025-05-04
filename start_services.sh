#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Start the AI Data API (e.g., FastAPI) in the background
echo "🔄 Starting AI API server..."
python3 ai_data_api.py &

# Capture the PID if you want to manage it later (optional)
API_PID=$!

# Wait briefly to ensure the API starts
sleep 2

# Start the Streamlit dashboard
echo "🚀 Launching Streamlit dashboard..."
streamlit run pages/api.py --server.enableCORS false --server.enableXsrfProtection false

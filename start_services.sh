#!/bin/bash

# Start the AI Data API (e.g., FastAPI) in the background
echo "🔄 Starting AI API server..."
python3 ai_data_api.py &

# Wait briefly to ensure the API starts
sleep 2

# Start the Streamlit dashboard
echo "🚀 Launching Streamlit dashboard..."
streamlit run api.py --server.enableCORS false --server.enableXsrfProtection false

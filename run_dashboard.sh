#!/bin/bash

# Indonesia Socioeconomic Dashboard Startup Script
# This script runs the Streamlit dashboard

echo "🇮🇩 Starting Indonesia Socioeconomic Dashboard..."
echo "📊 Loading data visualization components..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Install requirements if needed
if [ ! -f ".requirements_installed" ]; then
    echo "📦 Installing required packages..."
    pip install streamlit pandas plotly seaborn matplotlib numpy
    touch .requirements_installed
fi

# Start the dashboard
echo "🚀 Starting dashboard on http://localhost:8501"
echo "📱 The dashboard will open automatically in your browser"
echo "🛑 Press Ctrl+C to stop the dashboard"
echo ""

streamlit run dashboard.py

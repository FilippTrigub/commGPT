#!/bin/bash

# Run ChatWithTGChat.py in the background
python api/ChatWithTGChat.py &

# Run Streamlit app in the foreground
streamlit run frontend/Streamlit_UI.py --server.port 7100

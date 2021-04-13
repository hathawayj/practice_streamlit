mkdir -p ~/.streamlit

echo "\
[general]\n\
email = \"hathawayj@byui.edu\"\n\
" > ~/.streamlit/credentials.toml

echo "[server]
headless = true
enableCORS=false
port = $PORT
" > ~/.streamlit/config.toml
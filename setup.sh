mkdir -p ~/.streamlit/

echo "[general]
email = \"hathawayj@byui.edu\"
" > ~/.streamlit/credentials.toml

echo "[server]
headless = true
enableCORS=false
port = $PORT
" > ~/.streamlit/config.toml
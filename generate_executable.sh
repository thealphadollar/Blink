pyinstaller --noconfirm --log-level=WARN \
    --onefile --nowindow \
    --add-data="blink/.client_secrets:." \
    --add-data="blink/trackerList.json:." \
    --hidden-import=google-api-python-client \
    --log-level DEBUG \
    --paths blink:/home/thealphadollar/.local/share/virtualenvs/Blink-_KHfAu0d/ \
    blink/main.py
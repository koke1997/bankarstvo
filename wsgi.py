from app_factory import create_app, socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', allow_unsafe_werkzeug=True)
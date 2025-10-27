from app import create_app
import signal
import sys

app = create_app()

def signal_handler(sig, frame):
    print('\nServidor detenido correctamente (Ctrl+C)')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    print('Presiona Ctrl+C para detener el servidor')
    app.run(debug=True)

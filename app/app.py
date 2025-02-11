from flask import Flask, send_from_directory
import os
from utils.config_interface import ConfigInterface

app = Flask(__name__, static_folder='flask_static')

config = ConfigInterface()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index_route(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run()

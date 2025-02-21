from source.models.inventory import Inventory
from flask import Flask, jsonify
import os

app = Flask(__name__)


# Initialize the Inventory instance at startup
data_folder = os.path.join("source", "database")
inventory = Inventory(data_folder)


@app.route('/available-items', methods=['GET'])
def get_available_items():
    items = inventory.get_all_available_items()
    return jsonify(items)


if __name__ == '__main__':
    app.run(debug=True)
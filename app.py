import source.models.inventory
from flask import Flask, jsonify
from flask import request
import os

app = Flask(__name__)


# Initialize the Inventory instance at startup
data_folder = os.path.join("source", "database")
inventory = source.models.inventory.Inventory(data_folder)


@app.route('/available-items', methods=['GET'])
def get_available_items():
    items = inventory.get_all_available_items()
    return jsonify(items)


@app.route('/inventory', methods=['POST'])
def add_item():
    data = request.get_json()
    quantity = data['quantity']
    details = data['details']
    inventory.add_item(quantity, details)
    return jsonify({})


@app.route('/inventory', methods=['GET'])
def get_inventory():
    return inventory.get_inventory()


if __name__ == '__main__':
    app.run(debug=True)
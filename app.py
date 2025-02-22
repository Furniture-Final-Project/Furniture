import source.models.inventory
from flask import Flask, jsonify
from flask import request
import os
import schema 

app = Flask(__name__)

@app.route('/items', methods=['GET'])
def get_items():
    s = schema.session()
    results = s.query(schema.Furniture).all()

    items = [result.to_dict() for result in results]
    
    return jsonify({'items': items})


if __name__ == '__main__':
    app.run(debug=True)
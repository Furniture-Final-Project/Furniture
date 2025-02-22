import source.models.inventory
from flask import Flask, jsonify
from flask import request
import os
import schema 

def create_app(config: dict):
    app = Flask(__name__)

    schema.create(config['database_url'])

    @app.route('/items', methods=['GET'])
    def get_items():
        s = schema.session()
        results = s.query(schema.Furniture).all()
        items = { result.model_num: result.to_dict() for result in results}
        return jsonify({'items': items})

    
    return app
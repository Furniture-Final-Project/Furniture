import source.models.inventory
import flask
import os
import schema 

def create_app(config: dict):
    app = flask.Flask(__name__)

    schema.create(config['database_url'])

    @app.route('/items', methods=['GET'])
    def get_items():
        s = schema.session()
        query = s.query(schema.Furniture)
        category = flask.request.args.get('category')
        price = flask.request.args.get('max_price')
        model_num = flask.request.args.get('model_num')
        if category is not None:
            query = query.filter_by(category=category)
        if price is not None:
            price = int(price)
            query = query.filter(schema.Furniture.price<price)
        if model_num is not None:
            query = query.filter_by(model_num=model_num)
            
        results = query.all()
        items = { result.model_num: result.to_dict() for result in results}
        return flask.jsonify({'items': items})

    return app
    
    


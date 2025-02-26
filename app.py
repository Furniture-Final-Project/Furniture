import flask
import os
import schema 
import services


def create_app(config: dict):
    app = flask.Flask(__name__)

    schema.create(config['database_url'])

    @app.route('/items', methods=['GET'])
    def get_items():
        """
        Retrieves items from the furniture inventory.

        This function allows fetching items with optional filtering based on:
        - `category`: Filters items by category.
        - `max_price`: Returns only items priced below the given value.
        - `model_num`: Retrieves a specific item by model number.

        If `model_num` is provided, the response includes an `is_available` field:
        - `is_available: True` if the item has stock (stock_quantity > 0).
        - `is_available: False` if the item is out of stock (stock_quantity == 0).
        - This field is **only included** when retrieving a single item (`model_num` is specified).

        Returns:
            JSON response containing a dictionary of available items, 
            where keys are `model_num` and values are the item's full details.

        Example API Requests:
            - GET /items (retrieves all items)
            - GET /items?category=Chair (retrieves only chairs)
            - GET /items?max_price=500 (retrieves all items under $500)
            - GET /items?model_num=BD-5005 (retrieves a specific item, including `is_available`)

        This implementation ensures that the API response remains clean and context-aware,
        only including stock availability when relevant.
        """
        s = schema.session()
        query = s.query(schema.Furniture)

        category = flask.request.args.get('category')
        price = flask.request.args.get('max_price')
        model_num = flask.request.args.get('model_num')
        model_name = flask.request.args.get('model_name')

        if category is not None:
            query = query.filter_by(category=category)
        if price is not None:
            price = float(price)
            query = query.filter(schema.Furniture.price<price)
        if model_num is not None:
            query = query.filter_by(model_num=model_num)
        if model_name is not None:
            query = query.filter(schema.Furniture.model_name == model_name)
            
        results = query.all()

        # conditionally add "is_available" only if a specific model_num is requested 
        if model_num:
            items = {
                result.model_num: {**result.to_dict(), "is_available": result.stock_quantity > 0}
                for result in results
            }
        else: 
            items = { result.model_num: result.to_dict() for result in results}

        return flask.jsonify({'items': items})
    

    # TODO - Admin 
    @app.route('/admin/add_item', methods=['POST'])
    def add_item_endpoint():
        """
        API endpoint to add a new furniture item.
        """
        data = flask.request.get_json()  # Get JSON payload from the request
        s = schema.session()  # create a new session for DB operations
        services.add_item(s, data)  # call add_item from services.py
        return flask.jsonify({})
        
    
    @app.route('/admin/update_item', methods=['POST'])
    def update_item_endpoint():
        """
        API endpoint to add a new furniture item.
        """
        data = flask.request.get_json()  # Get JSON payload from the request
        s = schema.session()  # create a new session for DB operations
        services.update_item_quantity(s, data)  # call add_item from services.py
        return flask.jsonify({})
    
    @app.route('/admin/delete_item', methods=['POST'])
    def delete_item_endpoint():
        data = flask.request.get_json()
        s = schema.session()
        services.delete_item(s, data["model_num"])
        return flask.jsonify({})
    
    #============== User ====================
    @app.route('/users', methods=['GET'])
    def get_users():
        s = schema.session()
        query = s.query(schema.User)

        user_id = flask.request.args.get('user_id')
        if user_id is not None:
            query = query.filter_by(category=user_id)

        user = query.all()
        return flask.jsonify({'users': user})
    

    @app.route('/add_user', methods=['POST'])
    def add_users():
        """
        API endpoint to add a new furniture item.
        """
        data = flask.request.get_json()
        s = schema.session()  # ?? make sure it is connected to the User database
        return flask.jsonify({'users': user})



    return app  



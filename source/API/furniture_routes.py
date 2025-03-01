# from flask import Blueprint, jsonify
# from source.controller.furniture_inventory import get_furniture_price_details

# furniture_api = Blueprint("furniture_api", __name__)


# @furniture_api.route("/furniture/<int:model_num>", methods=["GET"])
# def get_furniture_price_info(model_num):
#     """API call to get furniture price basen on the model number"""
#     furniture_details = get_furniture_price_details(model_num)
#     if not furniture_details:
#         return jsonify({"error": "Item not found"}), 404

#     return jsonify(furniture_details)

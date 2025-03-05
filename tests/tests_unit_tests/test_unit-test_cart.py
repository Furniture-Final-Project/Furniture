# from datetime import datetime
# import pytest
# import http
# import schema
# from unittest.mock import patch
# from werkzeug.security import check_password_hash, generate_password_hash
# from source.models.OrderStatus import OrderStatus


# @pytest.mark.parametrize(
#     "user_exists, item_exists, expected",
#     [
#         (True, True, True),  # True
#         (False, True, False),  # False
#         (True, False, False),  # False
#         (False, False, False),  # False
#     ],
# )

# def test_update_quantity_with_item_not_in_cart(client):
#     """Test that updating a cart item is not possible if the item not in user's cart"""
#     update_info = dict(model_num="chair-0", user_id=1004, quantity=1)

#     # TODO: MOCKING
#     # login_info = {"user_name": "EmilyDavis", "password": "davisEmily!"}

#     response = client.post('/user/update_cart_item_quantity', json=update_info)
#     assert response.status_code == http.HTTPStatus.NOT_FOUND


# def test_valid_method_cartitem(user_exists, item_exists, expected):
#     """
#     Test the valid() function of CartItem.
#     It should return True only if both the user and item exist.
#     """
#     cart_item = schema.CartItem(user_id=9999, model_num="chair-10", quantity=1)

#     with (
#         patch("schema.user.get_user_details", return_value=user_exists),
#         patch("schema.cart.get_cart_item_full_details", return_value=item_exists),
#     ):

#         assert cart_item.valid() == expected


# def test_update_cart_item_quantity(client):
#     """
#     Test updating a cart item quantity and that the price updates.
#     """

#     update_info = dict(model_num="chair-0", user_id=1002, quantity=4)

#     # TODO: mock for login
#     # login_info = {"user_name": "JaneSmith", "password": "mypassword456"}

#     with patch("source.controller.cart.get_cart_item_full_details", return_value={update_info["model_num"]: {"stock_quantity": 5}}):
#         response = client.post('/user/update_cart_item_quantity', json=update_info)
#         assert response.status_code == http.HTTPStatus.OK

#     # Send a GET request to verify item stock update
#     response = client.get('/carts', query_string={"user_id": 1002})
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK

#     assert data["carts"]["1002"]["quantity"] == 4

#     assert data["carts"]['1002'] == {
#         'user_id': 1002,
#         'model_num': 'chair-0',
#         'quantity': 4,
#         'price_per_unit': 118.0,
#         'price': 472.0,
#         'model_name': 'Yosef',
#     }


# def test_updating_cart_item_quantity_to_0(client):
#     """Test updating a cart item quantity to 0 will delete it from the table"""
#     # Log in first to ensure the @login_required endpoint (/cart and /user/add_item_to_cart) can be accessed
#      # TODO: mock for login
#       # login_info = {"user_name": "JaneSmith", "password": "mypassword456"}

#     # Ensure the cart item in the cart
#     response = client.get('/carts', query_string={"user_id": 1002, 'model_num': 'chair-0'})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     cart = data['carts']
#     assert cart['1002'] == {'user_id': 1002, 'model_num': 'chair-0', 'quantity': 2, 'price_per_unit': 118.0, 'price': 236.0, 'model_name': 'Yosef'}

#     # update quantity to 0
#     update_info = dict(model_num="chair-0", user_id=1002, quantity=0)
#     response = client.post('/user/update_cart_item_quantity', json=update_info)
#     assert response.status_code == http.HTTPStatus.OK

#     # Send a GET request to verify item deleted successfully
#     response = client.get('/carts', query_string={"user_id": 1002, 'model_num': 'chair-0'})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     assert data['carts'] == {}

# def test_cart_get_all_cart_table(client):
#     """
#     Test retrieving all items in carts.

#     Sends a GET request to the '/carts' endpoint to fetch the complete list of shopping cart items.
#     Verifies that the response status is HTTP 200 OK. Ensures that all expected items are
#     returned, regardless of their stock status.

#     The test validates that:
#     - The response contains a 'carts' key.
#     - The number of unique items is as expected.
#     - Each cart item includes necessary details such as user ID, model number, and quantity.
#     """
#     # Authenticate as an admin to access detailed user data for verification.
#     # TODO: MOCKING
#     # login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}

#     response = client.get('/admin/carts')
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     carts = data['carts']
#     assert len(carts) == 1

#     assert carts['1002'] == {'user_id': 1002, 'model_num': 'chair-0', 'quantity': 2, 'price_per_unit': 118.0, 'price': 236.0, 'model_name': 'Yosef'}


# def test_cart_get_cart_by_userid(client):
#     """
#     Test retrieving a cart by user id.

#     send a GET request to the '/carts' with 'user_id' as a query parameter.
#     Verifies the response status is 200 OK and that the returned cart match
#     the specified user id.
#     :param client:
#     :return: Cart
#     """
#     # TODO: MOCKING for login
#     # login_info = {"user_name": "JaneSmith", "password": "mypassword456"}

#     response = client.get('/carts', query_string={"user_id": 1002})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     cart = data['carts']
#     assert len(cart) == 1

#     assert cart['1002'] == {'user_id': 1002, 'model_num': 'chair-0', 'quantity': 2, 'price_per_unit': 118.0, 'price': 236.0, 'model_name': 'Yosef'}
#     assert data['cart_total_price'] == 236.0

# def test_get_specific_item_in_cart(client):
#     """
#     Test retrieving an item by model number and user id.
#     """
#     # TODO: MOCKING for login
#     # login_info = {"user_name": "JaneSmith", "password": "mypassword456"}

#     response = client.get('/carts', query_string={"user_id": 1002, 'model_num': 'chair-0'})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     cart = data['carts']
#     assert len(cart) == 1

#     assert cart['1002'] == {'user_id': 1002, 'model_num': 'chair-0', 'quantity': 2, 'price_per_unit': 118.0, 'price': 236.0, 'model_name': 'Yosef'}

# def test_delete_cart_item(client):
#     """Test deleting a cart item from CartItem table"""
#     # TODO: MOCKING for login
#     # login_info = {"user_name": "JaneSmith", "password": "mypassword456"}

#     # Ensure the cart item in the cart
#     response = client.get('/carts', query_string={"user_id": 1002, 'model_num': 'chair-0'})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     cart = data['carts']
#     assert cart['1002'] == {'user_id': 1002, 'model_num': 'chair-0', 'quantity': 2, 'price_per_unit': 118.0, 'price': 236.0, 'model_name': 'Yosef'}

#     delete_item = {'model_num': 'chair-0', 'user_id': 1002}
#     # Send a POST request to delete the item
#     response = client.post('/user/delete_cart_item', json=delete_item)
#     assert response.status_code == http.HTTPStatus.OK

#     # Send a GET request to verify item deleted successfully
#     response = client.get('/carts', query_string={"user_id": 1002, 'model_num': 'chair-0'})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     assert data['carts'] == {}

# import source.controller.user as user


# # unit test: test_get_user_details_existing - it was in test_app.py and moved here 
# # we need to make sure it runs correctly  
# def test_get_user_details_existing():
#     """Test retrieving details of an existing user from the test database"""
#     user_id = 1003
#     user_data = user.get_user_details(user_id)

#     assert user_data["user_id"] == 1003
#     assert user_data["user_name"] == "MichaelBrown"
#     assert user_data["user_full_name"] == "Michael Brown"
#     assert user_data["user_phone_num"] == "555-5678"
#     assert user_data["address"] == "789 Maple Street, Los Angeles, CA"
#     assert user_data["email"] == "michaelbrown@example.com"
#     assert user_data["role"] == "user"

#========================================================================================
# def test_get_user_by_id(client):
#     # TODO: mock for admin
    
#     response = client.get('/admin/users', query_string={"user_id": 1002})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     users = data['users']
#     assert len(users) == 1
#     assert users['1002']["user_id"] == 1002
#     assert users['1002']["user_name"] == "JaneSmith"
#     assert users['1002']["user_full_name"] == "Jane Smith"
#     assert users['1002']["user_phone_num"] == "555-1234"
#     assert users['1002']["address"] == "456 Oak Avenue, New York, NY"
#     assert users['1002']["email"] == "janesmith@example.com"
#     assert users['1002']["role"] == "user"
#     hashed_password = users['1002']["password"]
#     assert hashed_password != "mypassword456"
#     assert check_password_hash(hashed_password, "mypassword456")


# def test_add_new_user(client):
#     user_info = {
#         "user_id": 207105880,
#         "user_name": "JonCohen",
#         "user_full_name": "Jon Cohen",
#         "user_phone_num": "555-7824",
#         "address": "123 Elm Street, Springfield, IL",
#         "email": "johndoe@example.com",
#         "password": "securepassword123",
#         "role": "user",
#     }
#     response = client.post('/add_user', json=user_info)
#     assert response.status_code == http.HTTPStatus.OK

#     # TODO: mock for admin

#     # Send a GET request to verify user was asses successfully
#     response = client.get('/admin/users', query_string={"user_id": 207105880})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     assert data["users"]['207105880']["user_name"] == "JonCohen"


# def test_password_hashing(client):
#     user_info = {
#         "user_id": 67890,
#         "user_name": "AliceDoe",
#         "user_full_name": "Alice Doe",
#         "user_phone_num": "555-8821",
#         "address": "789 Oak St, New York, NY",
#         "email": "alicedoe@example.com",
#         "password": "mypassword123",
#         "role": "user",
#     }

#     response = client.post('/add_user', json=user_info)
#     assert response.status_code == http.HTTPStatus.OK

#     # TODO: mock for admin

#     response = client.get('/admin/users', query_string={"user_id": 67890})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()

#     hashed_password = data["users"]["67890"]["password"]
#     assert hashed_password != user_info["password"]
#     assert check_password_hash(hashed_password, user_info["password"])


# def test_add_admin_user(client):
#     user_info = {
#         "user_id": 207105881,
#         "user_name": "RonCohen",
#         "user_full_name": "Ron Cohen",
#         "user_phone_num": "555-7824",
#         "address": "120 Elm Street, Springfield, IL",
#         "email": "johndoe@example.com",
#         "password": "securepassword123",
#         "role": "admin",
#     }
#     response = client.post('/add_admin_user', json=user_info)
#     assert response.status_code == http.HTTPStatus.OK

#     # TODO: mock for admin

#     # Send a GET request to verify user was asses successfully
#     response = client.get('/admin/users', query_string={"user_id": 207105881})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     assert data["users"]['207105881']["user_name"] == "RonCohen"


# def test_add_admin_user_invalid(client):
#     """
#     Ensures '/add_admin_user' returns 400 BAD REQUEST if 'role' is 'user',
#     and verifies no user is created.
#     """
#     user_info = {
#         "user_id": 207105881,
#         "user_name": "RonCohen",
#         "user_full_name": "Ron Cohen",
#         "user_phone_num": "555-7824",
#         "address": "120 Elm Street, Springfield, IL",
#         "email": "johndoe@example.com",
#         "password": "securepassword123",
#         "role": "user",
#     }
#     response = client.post('/add_admin_user', json=user_info)
#     assert response.status_code == http.HTTPStatus.BAD_REQUEST

#     # TODO: mock for admin

#     # Send a GET request to verify user was asses successfully
#     response = client.get('/admin/users', query_string={"user_id": 207105881})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     assert data["users"] == {}


# def test_add_user_invalid_role(client):
#     """
#         Ensures '/add_user' returns 400 BAD REQUEST if 'role' is 'admin',
#     and verifies no user is created.
#     """
#     user_info = {
#         "user_id": 207105881,
#         "user_name": "RonCohen",
#         "user_full_name": "Ron Cohen",
#         "user_phone_num": "555-7824",
#         "address": "120 Elm Street, Springfield, IL",
#         "email": "johndoe@example.com",
#         "password": "securepassword123",
#         "role": "admin",
#     }
#     response = client.post('/add_user', json=user_info)
#     assert response.status_code == http.HTTPStatus.BAD_REQUEST

#     # TODO: mock for admin

#     # Send a GET request to verify user was asses successfully
#     response = client.get('/admin/users', query_string={"user_id": 207105881})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     assert data["users"] == {}


# def test_user_update_address(client):
#     """Test to update address of a user, by its user_id"""
#     updated_info = {"user_id": 1003, "address": "21 Yaakov Meridor, Tel Aviv"}
#     response = client.post('/update_user', json=updated_info)
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK

#     # TODO: mock for admin 

#     # Send a GET request to verify user details were updated corretly
#     response = client.get('/admin/users', query_string={"user_id": 1003})
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK
#     assert data["users"]['1003']["address"] == "21 Yaakov Meridor, Tel Aviv"


# def test_user_update_user_name(client):
#     """Test to update user_name of a user, by its user_id"""
#     update_info = {"user_id": 1003, "user_name": "Michael_Cohen"}
#     response = client.post('/update_user', json=update_info)
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK

#     # TODO: mock for admin 

#     # Send a GET request to verify user details were updated correctly
#     response = client.get('/admin/users', query_string={"user_id": 1003})
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK
#     assert data["users"]['1003']["user_name"] == "Michael_Cohen"


# def test_user_update_user_full_name(client):
#     """Test to update user_full_name of a user, by its user_id"""
#     update_info = {"user_id": 1003, "user_full_name": "Michael Levi"}
#     response = client.post('/update_user', json=update_info)
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK

#     # TODO: mock for admin 

#     # Send a GET request to verify user details were updated correctly
#     response = client.get('/admin/users', query_string={"user_id": 1003})
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK
#     assert data["users"]['1003']["user_full_name"] == "Michael Levi"


# def test_user_update_user_phone_num(client):
#     """Test to update user_phone_num of a user, by its user_id"""
#     update_info = {"user_id": 1003, "user_phone_num": "555-1094"}
#     response = client.post('/update_user', json=update_info)
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK

      # TODO: mock for admin 

#     # Send a GET request to verify user details were updated correctly
#     response = client.get('/admin/users', query_string={"user_id": 1003})
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK
#     assert data["users"]['1003']["user_phone_num"] == "555-1094"

# def test_user_update_email(client):
#     """Test to update email of a user, by its user_id"""
#     update_info = {"user_id": 1003, "email": "MichaelCohen@gmail.com"}
#     response = client.post('/update_user', json=update_info)
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK

      # TODO: mock for admin 

#     # Send a GET request to verify user details were updated correctly
#     response = client.get('/admin/users', query_string={"user_id": 1003})
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK
#     assert data["users"]['1003']["email"] == "MichaelCohen@gmail.com"


# def test_user_update_password(client):
#     """Test to update password of a user and hash it, by its user_id"""
#     update_info = {"user_id": 1003, "password": "NewSecurePass123"}
#     response = client.post('/update_user', json=update_info)
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK

      # TODO: mock for admin 

#     # Send a GET request to verify user details were updated correctly
#     response = client.get('/admin/users', query_string={"user_id": 1003})
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK
#     hashed_password = data["users"]['1003']["password"]
#     # Verify that the new password saved as hash password
#     assert hashed_password != "NewSecurePass123"
#     assert check_password_hash(hashed_password, "NewSecurePass123")

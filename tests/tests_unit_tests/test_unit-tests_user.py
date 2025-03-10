import pytest
import functools
import schema
import http
import source.controller.user as user

# related to the DB
from werkzeug.security import check_password_hash, generate_password_hash

# from source.models.OrderStatus import OrderStatus
# from datetime import datetime


@pytest.fixture(autouse=True)
def bypass_admin_required(monkeypatch):
    """
    Automatically bypass the admin_required decorator for testing.

    This fixture defines a dummy decorator that simply calls the original function,
    effectively bypassing admin authentication. It then patches the app's admin_required
    decorator with this dummy version before any routes are created.
    """

    def dummy_decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    # Import app after defining the dummy decorator to ensure patching is applied
    import app

    monkeypatch.setattr(app, 'admin_required', dummy_decorator)


@pytest.fixture(autouse=True)
def bypass_login_required(monkeypatch):
    """
    Automatically bypass the login_required decorator for testing.

    Similar to bypass_admin_required, this fixture defines a dummy decorator
    that ignores the login check and directly calls the decorated function.
    """

    def dummy_decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    import app

    monkeypatch.setattr(app, 'login_required', dummy_decorator)


@pytest.fixture
def application():
    import app

    application = app.create_app({'database_url': f'sqlite:///:memory:'})  # Use in-memory DB for testing
    yield application


@pytest.fixture
def client(application):
    with application.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def preprepared_data(application):
    session = schema.session()
    chair0 = schema.Furniture(
        model_num='chair-0',
        model_name='Yosef',
        description='a nice chair',
        price=100.0,
        dimensions={"height": 90, "width": 45, "depth": 50},
        category="Chair",
        image_filename='classic_wooden_chair.jpg',
        stock_quantity=3,
        discount=0.0,
        details={'material': 'wood', 'weight': 5, 'color': 'white'},
    )
    chair1 = schema.Furniture(
        model_num='chair-1',
        model_name='Haim',
        description='a Very nice chair',
        price=200.0,
        dimensions={"height": 90, "width": 45, "depth": 50},
        category="Chair",
        image_filename='classic_wooden_chair.jpg',
        stock_quantity=4,
        discount=0.0,
        details={'material': 'wood', 'weight': 6, 'color': 'white'},
    )
    bed = schema.Furniture(
        model_num="BD-5005",
        model_name="DreamComfort",
        description="A luxurious memory foam bed with a sturdy solid wood frame.",
        price=1200.0,
        dimensions={"height": 50, "width": 160, "depth": 200},
        category="Bed",
        image_filename="memory_foam_bed.jpg",
        stock_quantity=5,
        discount=10.0,
        details={"mattress_type": "Memory Foam", "frame_material": "Solid Wood"},
    )
    bookshelf = schema.Furniture(
        model_num="BS-4004",
        model_name="OakElegance",
        description="A stylish and durable bookshelf made of pine wood with a natural oak finish.",
        price=110.0,
        dimensions={"height": 180, "width": 80, "depth": 30},
        category="BookShelf",
        image_filename="oak_bookshelf.jpg",
        stock_quantity=0,
        discount=50.0,
        details={"num_shelves": 5, "max_capacity_weight_per_shelf": 20.0, "material": "Pine Wood", "color": "Natural Oak"},
    )
    sofa = schema.Furniture(
        model_num="SF-3003",
        model_name="LuxComfort",
        description="A luxurious three-seater sofa with top-grain leather upholstery, perfect for a modern living room.",
        price=1200.0,
        dimensions={"height": 85, "width": 220, "depth": 95},
        category="Sofa",
        image_filename="luxury_leather_sofa.jpg",
        stock_quantity=5,
        discount=10.0,
        details={"upholstery": "Top-Grain Leather", "color": "Dark Gray", "num_seats": 3},
    )

    user_1 = schema.User(
        user_id=1002,
        user_name="JaneSmith",
        user_full_name="Jane Smith",
        user_phone_num="555-1234",
        address="456 Oak Avenue, New York, NY",
        email="janesmith@example.com",
        password=generate_password_hash("mypassword456"),
        role="user",
    )

    user_2 = schema.User(
        user_id=1003,
        user_name="MichaelBrown",
        user_full_name="Michael Brown",
        user_phone_num="555-5678",
        address="789 Maple Street, Los Angeles, CA",
        email="michaelbrown@example.com",
        password=generate_password_hash("brownieM123"),
        role="user",
    )

    user_3 = schema.User(
        user_id=1004,
        user_name="EmilyDavis",
        user_full_name="Emily Davis",
        user_phone_num="555-9012",
        address="101 Pine Road, Austin, TX",
        email="emilydavis@example.com",
        password=generate_password_hash("davisEmily!"),
        role="user",
    )

    user_4 = schema.User(
        user_id=1005,
        user_name="RobertWilson",
        user_full_name="Robert Wilson",
        user_phone_num="555-3456",
        address="202 Birch Lane, Seattle, WA",
        email="robertwilson@example.com",
        password=generate_password_hash("wilsonRob007"),
        role="admin",
    )

    session.add_all([chair0, chair1, bed, bookshelf, sofa, user_1, user_2, user_3, user_4])
    session.commit()
    yield


def test_get_user_details_existing():
    """
    Test retrieving details of an existing user from the test database.

    Steps:
    - Calls `get_user_details()` with an existing user ID.
    - Verifies that the retrieved user details match expected values.
    """
    user_id = 1003
    user_data = user.get_user_details(user_id)

    assert user_data["user_id"] == 1003
    assert user_data["user_name"] == "MichaelBrown"
    assert user_data["user_full_name"] == "Michael Brown"
    assert user_data["user_phone_num"] == "555-5678"
    assert user_data["address"] == "789 Maple Street, Los Angeles, CA"
    assert user_data["email"] == "michaelbrown@example.com"
    assert user_data["role"] == "user"


def test_get_user_by_id(client):
    """
        Test retrieving a specific user by ID.

        Steps:
        - Sends a GET request to '/admin/users' with a specific user ID.
        - Verifies the response status is HTTP 200 OK.
        - Ensures the response contains correct user details.
        """

    response = client.get('/admin/users', query_string={"user_id": 1002})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    users = data['users']
    assert len(users) == 1
    assert users['1002']["user_id"] == 1002
    assert users['1002']["user_name"] == "JaneSmith"
    assert users['1002']["user_full_name"] == "Jane Smith"
    assert users['1002']["user_phone_num"] == "555-1234"
    assert users['1002']["address"] == "456 Oak Avenue, New York, NY"
    assert users['1002']["email"] == "janesmith@example.com"
    assert users['1002']["role"] == "user"
    hashed_password = users['1002']["password"]
    assert hashed_password != "mypassword456"
    assert check_password_hash(hashed_password, "mypassword456")


def test_add_new_user(client):
    """
        Test adding a new user to the system.

        Steps:
        - Sends a POST request to '/add_user' with valid user details.
        - Verifies the response status is HTTP 200 OK.
        - Retrieves the newly added user and ensures the details are correct.
        """

    user_info = {
        "user_id": 207105880,
        "user_name": "JonCohen",
        "user_full_name": "Jon Cohen",
        "user_phone_num": "555-7824",
        "address": "123 Elm Street, Springfield, IL",
        "email": "johndoe@example.com",
        "password": "securepassword123",
        "role": "user",
    }
    response = client.post('/add_user', json=user_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user was asses successfully
    response = client.get('/admin/users', query_string={"user_id": 207105880})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    assert data["users"]['207105880']["user_name"] == "JonCohen"


def test_password_hashing(client):
    """
        Test that user passwords are properly hashed.

        Steps:
        - Adds a new user with a known password.
        - Retrieves the user data and ensures that the stored password is hashed.
        - Checks if the hashed password matches the original password using `check_password_hash()`.
        """

    user_info = {
        "user_id": 67890,
        "user_name": "AliceDoe",
        "user_full_name": "Alice Doe",
        "user_phone_num": "555-8821",
        "address": "789 Oak St, New York, NY",
        "email": "alicedoe@example.com",
        "password": "mypassword123",
        "role": "user",
    }

    response = client.post('/add_user', json=user_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.get('/admin/users', query_string={"user_id": 67890})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()

    hashed_password = data["users"]["67890"]["password"]
    assert hashed_password != user_info["password"]
    assert check_password_hash(hashed_password, user_info["password"])


def test_add_admin_user(client):
    """
        Test adding a new admin user to the system.

        Steps:
        - Sends a POST request to '/add_admin_user' with valid admin user details.
        - Verifies the response status is HTTP 200 OK.
        - Retrieves the newly added admin user and ensures the details are correct.
        """
    user_info = {
        "user_id": 207105881,
        "user_name": "RonCohen",
        "user_full_name": "Ron Cohen",
        "user_phone_num": "555-7824",
        "address": "120 Elm Street, Springfield, IL",
        "email": "johndoe@example.com",
        "password": "securepassword123",
        "role": "admin",
    }
    response = client.post('/add_admin_user', json=user_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user was asses successfully
    response = client.get('/admin/users', query_string={"user_id": 207105881})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    assert data["users"]['207105881']["user_name"] == "RonCohen"


def test_add_admin_user_invalid(client):
    """
    Test that an invalid admin user cannot be created.

    Steps:
    - Attempts to add an admin user with an invalid role ('user').
    - Verifies that the server returns HTTP 400 BAD REQUEST.
    - Ensures that no user was created in the system.
    """
    user_info = {
        "user_id": 207105881,
        "user_name": "RonCohen",
        "user_full_name": "Ron Cohen",
        "user_phone_num": "555-7824",
        "address": "120 Elm Street, Springfield, IL",
        "email": "johndoe@example.com",
        "password": "securepassword123",
        "role": "user",
    }
    response = client.post('/add_admin_user', json=user_info)
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Send a GET request to verify user was asses successfully
    response = client.get('/admin/users', query_string={"user_id": 207105881})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    assert data["users"] == {}


def test_add_user_invalid_role(client):
    """
    Test that a regular user cannot be created with the 'admin' role.

    Steps:
    - Attempts to add a user with the role set to 'admin'.
    - Verifies that the server returns HTTP 400 BAD REQUEST.
    - Ensures that no user was created in the system.
    """
    user_info = {
        "user_id": 207105881,
        "user_name": "RonCohen",
        "user_full_name": "Ron Cohen",
        "user_phone_num": "555-7824",
        "address": "120 Elm Street, Springfield, IL",
        "email": "johndoe@example.com",
        "password": "securepassword123",
        "role": "admin",
    }
    response = client.post('/add_user', json=user_info)
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Send a GET request to verify user was asses successfully
    response = client.get('/admin/users', query_string={"user_id": 207105881})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    assert data["users"] == {}


def test_user_update_address(client):
    """
    Test updating a user's address.

    Steps:
    - Sends a POST request to '/update_user' with a new address.
    - Verifies the response status is HTTP 200 OK.
    - Retrieves the updated user data to confirm the change.
    """

    updated_info = {"user_id": 1003, "address": "21 Yaakov Meridor, Tel Aviv"}
    response = client.post('/update_user', json=updated_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated corretly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["address"] == "21 Yaakov Meridor, Tel Aviv"


def test_user_update_user_name(client):
    """
    Test updating a user's username.

    Steps:
    - Sends a POST request to '/update_user' with a new username.
    - Verifies the response status is HTTP 200 OK.
    - Retrieves the updated user data to confirm the change.
    """

    update_info = {"user_id": 1003, "user_name": "Michael_Cohen"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated correctly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["user_name"] == "Michael_Cohen"


def test_user_update_user_full_name(client):
    """
    Test updating a user's full name.

    Steps:
    - Sends a POST request to '/update_user' with a new full name.
    - Verifies the response status is HTTP 200 OK.
    - Retrieves the updated user data to confirm the change.
    """

    update_info = {"user_id": 1003, "user_full_name": "Michael Levi"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated correctly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["user_full_name"] == "Michael Levi"


def test_user_update_user_phone_num(client):
    """
    Test updating a user's phone number.

    Steps:
    - Sends a POST request to '/update_user' with a new phone number.
    - Verifies the response status is HTTP 200 OK.
    - Retrieves the updated user data to confirm the change.
    """

    update_info = {"user_id": 1003, "user_phone_num": "555-1094"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated correctly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["user_phone_num"] == "555-1094"


def test_user_update_email(client):
    """
    Test updating a user's email.

    Steps:
    - Sends a POST request to '/update_user' with a new email.
    - Verifies the response status is HTTP 200 OK.
    - Retrieves the updated user data to confirm the change.
    """

    update_info = {"user_id": 1003, "email": "MichaelCohen@gmail.com"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated correctly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["email"] == "MichaelCohen@gmail.com"


def test_user_update_password(client):
     """
    Test updating and hashing a user's password.

    Steps:
    - Sends a POST request to '/update_user' with a new password.
    - Verifies the response status is HTTP 200 OK.
    - Retrieves the updated user data and checks that the password is hashed.
    - Confirms that the hashed password matches the original password using `check_password_hash()`.
    """

    update_info = {"user_id": 1003, "password": "NewSecurePass123"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated correctly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    hashed_password = data["users"]['1003']["password"]
    # Verify that the new password saved as hash password
    assert hashed_password != "NewSecurePass123"
    assert check_password_hash(hashed_password, "NewSecurePass123")

## Group 004 - Online Furniture Store

### Group Members:
Maya Rozin, Rotem Rand, Talya Peretz, Noam Schneider, Maya Berger

## Root Convention

All commands are [assumed to run from the root of the project] - the directory in which _this README_ is located.
---

### Project Description:
This project is an integrated system designed to manage an inventory system with user accounts, shopping cart functionality, website search features, and more. It facilitates a smooth and efficient experience for both administrators managing stock and orders and users interacting with the e-commerce platform. The core functionalities include inventory management by admins, detailed user profiles, and a dynamic shopping cart that seamlessly tracks orders and purchases.

---

### Technology Stack:
- **Python**: The sole programming language used.
- **SQLAlchemy**: An ORM used for robust database interactions.
- **SQLite**: Chosen for its simplicity and ease of setup in handling the inventory, user data, and shopping cart information.

---

### Design and Implementation:
The project follows a modular design by separating concerns into distinct layers such as the data access layer, business logic, and presentation. The SQLite database, interfaced through SQLAlchemy, facilitates straightforward data manipulation while ensuring future scalability. The design allows for easy migration to more robust database solutions if needed. Key design highlights include clear entity relationships, built-in data validation, and a focus on maintainable code architecture.

---

### Design Patterns:
1. **Data Mapper Pattern:** Implemented using SQLAlchemy's declarative base, this pattern separates the in-memory representation of objects from the underlying database schema, allowing independent data management.
2. **Strategy Pattern:** Applied in the payment processing system, allowing interchangeable payment methods such as CreditCardPayment and PayPalPayment without altering the core logic.
3. **Decorator Pattern:** Used for authentication and authorization through decorators like `login_required` and `admin_required` to manage access control logic.
4. **Use of ENUMs:** Utilized for defining fixed sets of constant values like order statuses (`PENDING, SHIPPED, DELIVERED, CANCELLED`) and payment methods (`CREDIT_CARD, PAYPAL, BANK_TRANSFER`).

---

### Setup Instructions:

#### 1. Install Requirements
```bash
pip install -r requirements.txt
```

#### 2. Loading Sample Data into the Database
This repository includes a file `sample_data.db`, an SQLite database with sample data.
To use it when running the server, copy this file to `default.db` before running the server.

##### On Mac:
```bash
cp sample_data.db default.db
waitress-serve --call app:create_app
```

##### On Windows:
```bash
copy sample_data.db default.db
waitress-serve --call app:create_app
```

#### 3. Running the Server
```bash
waitress-serve --call app:create_app
```

---

### API Documentation:

#### API Implementation Notes:
Initially, *POST* was used for both updating (`/admin/update_item`) and deleting (`/admin/delete_item`) resources. Later, it was realized that a fully RESTful design should use *PUT* for updates and *DELETE* for removals. However, refactoring was deemed unnecessary at the advanced stage of the project.

While this does not fully align with RESTful best practices, the implementation remains functional. Given more time, these endpoints would be restructured to follow standard conventions.

---
## Examples of designed API calls:


### 1. Get Items from Inventory
#### **Endpoint:**
```
GET /items
```
#### **Description:**
Retrieves furniture items from the inventory with optional filtering.

#### **Query Parameters:**
| Parameter   | Type   | Required | Description  |
|------------|--------|----------|-------------|
| `category`  | string | No       | Filter items by category (e.g., `Chair`, `Table`). |
| `max_price` | float  | No       | Retrieve items below the given price. |
| `model_num` | string | No       | Retrieve a specific item by model number. |

#### **Example Requests:**
- Get all items: `GET /items`
- Get chairs under $500: `GET /items?category=Chair&max_price=500`
- Get a specific model: `GET /items?model_num=chair-0`

#### **Response:**
```json
{
  "items": {
    "chair-0": {
      "model_num": "chair-0",
      "model_name": "Yosef",
      "description": "a nice chair",
      "price": 100.0,
      "final_price": 118.0,
      "dimensions": {"height": 90, "width": 45, "depth": 50},
      "category": "Chair",
      "image_filename": "classic_wooden_chair.jpg",
      "stock_quantity": 3,
      "discount": 0.0,
      "details": {"material": "wood", "weight": 5, "color": "white"}
    }
  }
}
```

---

### 2. Add an Item to Shopping Cart (Requires Login)
#### **Endpoint:**
```
POST /user/add_item_to_cart
```
#### **Authentication:**
**Login Required**

#### **Description:**
Allows a logged-in user to add an item to their shopping cart.

#### **Request Body (JSON):**
```json
{
  "user_id": 1003,
  "model_num": "chair-1",
  "quantity": 1
}
```

#### **Response:**
Returns `200 OK` when updated successfully.

#### **Error Responses:**
| HTTP Status | Error Message |
|------------|---------------|
| 400 Bad Request | If required fields are missing. |
| 401 Unauthorized | If user is not logged in. |
| 404 Not Found | If the item does not exist in inventory. |
| 409 Conflict | If not enough stock is available. |

---

### 3. Checkout and Process Order
#### **Endpoint:**
```
POST /checkout
```
#### **Description:**
Processes a user's order, handling:
- **Cart validation** (ensuring items are in stock).
- **Payment processing** (using a selected strategy).
- **Order creation** (returns an `order_id` if successful).
- **Inventory update** (reduces stock for purchased items).
- **Cart cleanup** (removes items from cart after purchase).

#### **Request Body (JSON):**
```json
{
  "user_id": 123,
  "address": "123 Elm Street, NY",
  "payment_method": "credit_card"
}
```

#### **Response (Success):**
```json
{
  "order_id": 98765,
  "status": "confirmed",
  "total_price": 890.50
}
```

#### **Error Responses:**
| HTTP Status | Error Message |
|------------|---------------|
| 400 Bad Request | "Invalid address. Please provide a valid shipping address." |
| 404 Not Found | "Cart for user {user_id} is empty!" |
| 409 Conflict | "Not enough stock available, stock quantity is {available_stock}" |
| 402 Payment Required | "Payment was declined. Please try another payment method." |
| 500 Internal Server Error | "Failed to create order." |

---

### Notes on Implementation:
- Payment strategy is injected into CheckoutService, supporting different methods (e.g., credit card, PayPal).
- If cart items exceed stock, checkout is halted.
- If order creation fails, it returns `500`.
- The cart is cleared upon successful checkout.

----
## Full API documantation:

# API Documentation - Online Furniture Store

## Introduction

The API for the online furniture store allows users to perform various operations, including user management, orders, shopping cart operations, checkout, and inventory management.

All requests to the API should be made using **JSON**, and responses are returned in **JSON** format.

---

# 1. API Endpoint: Retrieve Items from Inventory

## **Endpoint Details**
- **URL:** '/items'
- **Method:** 'GET'
- **Description:** Retrieves items from the furniture inventory with optional filtering.

## **Query Parameters**
- 'category' (string): Filter items by category.
- 'max_price' (float): Retrieve only items priced below the given value.
- 'model_num' (string): Retrieve a specific item by model number.
- 'model_name' (string): Retrieve a specific item by model name.

## **Response Details**
- Returns a JSON dictionary of available furniture items.


# 2. API Endpoint: Add New Furniture Item

## **Endpoint Details**
- **URL:** '/admin/add_item'
- **Method:** 'POST'
- **Authentication:** Admin Only
- **Description:** Adds a new furniture item to the inventory.

## **Request Body (JSON)**
- 'model_num' (string, required): Unique identifier for the furniture item.
- 'name' (string, required): Name of the furniture item.
- 'category' (string, required): Category of the furniture item (e.g., Chair, Table).
- 'price' (float, required): Price of the item.
- 'stock_quantity' (integer, required): Number of available units.
- 'description' (string, optional): Additional details about the furniture item.

## **Response Details**
- Returns an empty JSON response ('{}') upon successful addition.

## **Example API Request**
```json
{
    "model_num": "SOFA-123",
    "name": "Luxury Sofa",
    "category": "Sofa",
    "price": 3200.00,
    "stock_quantity": 10,
    "description": "A premium luxury sofa with high-end fabric."
}
```

## **Example API Response**
```json
{}
```

## **Notes**
- This endpoint requires **Admin privileges**.
- The request must be sent with a **valid JSON payload**.


# 3. API Endpoint: Update Furniture Item Quantity

## **Endpoint Details**
- **URL:** '/admin/update_item'
- **Method:** 'POST'
- **Authentication:** Admin Only
- **Description:** Updates the quantity of an existing furniture item in the inventory.

## **Request Body (JSON)**
- 'model_num' (string, required): Unique identifier of the furniture item.
- 'stock_quantity' (integer, required): New quantity of the item in stock.

## **Response Details**
- Returns an empty JSON response ('{}') upon successful update.

## **Example API Request**
```json
{
    "model_num": "SOFA-123",
    "stock_quantity": 15
}
```

## **Example API Response**
```json
{}
```

## **Notes**
- This endpoint requires **Admin privileges**.
- The request must be sent with a **valid JSON payload**.
- If the provided 'model_num' does not exist, the request will not update any item.


# 4. API Endpoint: Delete Furniture Item

## **Endpoint Details**
- **URL:** '/admin/delete_item'
- **Method:** 'POST'
- **Authentication:** Admin Only
- **Description:** Deletes an existing furniture item from the inventory.

## **Request Body (JSON)**
- 'model_num' (string, required): Unique identifier of the furniture item to be deleted.

## **Response Details**
- Returns an empty JSON response ('{}') upon successful deletion.

## **Example API Request**
```json
{
    "model_num": "SOFA-123"
}
```

## **Example API Response**
```json
{}
```

## **Notes**
- This endpoint requires **Admin privileges**.
- If the provided 'model_num' does not exist, the request will not delete any item.
- The request must be sent with a **valid JSON payload**.


# 5. API Endpoint: Update Furniture Item Discount

## **Endpoint Details**
- **URL:** '/admin/update_discount'
- **Method:** 'POST'
- **Authentication:** Admin Only
- **Description:** Updates the discount percentage of an existing furniture item.

## **Request Body (JSON)**
- 'model_num' (string, required): Unique identifier of the furniture item.
- 'discount' (float, required): New discount percentage (must be between 0 and 100).

## **Response Details**
- **200 OK**: If the discount was successfully updated.
- **400 BAD REQUEST**: If required fields are missing or if the discount is not within the valid range (0-100).
- **404 NOT FOUND**: If the specified item does not exist.

## **Example API Request**
```json
{
    "model_num": "chair-1",
    "discount": 15.0
}
```

## **Example API Response (Successful Update)**
```json
{}
```

## **Example API Response (Missing Fields)**
```json
{
    "error": "Missing required fields"
}
```

## **Example API Response (Invalid Discount Range)**
```json
{
    "error": "Discount must be between 0 to 100"
}
```

## **Notes**
- This endpoint requires **Admin privileges**.
- The 'discount' value must be strictly between **0 and 100**.
- If the provided 'model_num' does not exist, the request will return a '404 NOT FOUND' error.
- The request must be sent with a **valid JSON payload**.


# 6. API Endpoint: Retrieve User List

## **Endpoint Details**
- **URL:** '/admin/users'
- **Method:** 'GET'
- **Authentication:** Admin Only
- **Description:** Retrieves a list of registered users. Can filter by 'user_id'.

## **Query Parameters (Optional)**
- 'user_id' (integer): Retrieve a specific user by their ID.

## **Response Details**
- Returns a JSON dictionary of user details.
- If 'user_id' is provided, only the specified user will be returned.

## **Notes**
- This endpoint requires **Admin privileges**.
- If 'user_id' is specified but does not exist, the response will return an empty dictionary.
- The request must be properly authenticated.


# 7. API Endpoint: Register a New User

## **Endpoint Details**
- **URL:** '/add_user'
- **Method:** 'POST'
- **Authentication:** Not required
- **Description:** Creates a new user account in the system.

## **Request Body (JSON)**
- 'user_id' (integer, required): Unique identifier for the user.
- 'user_name' (string, required): Username for login.
- 'user_full_name' (string, required): Full name of the user.
- 'user_phone_num' (string, required): Contact phone number.
- 'address' (string, required): User's physical address.
- 'email' (string, required): Email address for communication.
- 'password' (string, required): Secure password for authentication.
- 'role' (string, required): Must be set to '"user"'.

## **Response Details**
- **200 OK**: If the user was successfully created.
- **400 BAD REQUEST**: If any required field is missing or if 'role' is not '"user"'.

## **Example API Request**
```json
{
    "user_id": 123,
    "user_name": "noam_schneider",
    "user_full_name": "Noam Schneider",
    "user_phone_num": "0501234567",
    "address": "123 Main St, Tel Aviv",
    "email": "noam@example.com",
    "password": "SecurePass123",
    "role": "user"
}
```

## **Example API Response (Successful Registration)**
```json
{}
```

## **Example API Response (Missing Fields or Invalid Role)**
```json
{
    "success": false,
    "message": "Either one or more required fields are missing, or 'role' is not set to 'user'."
}
```

## **Notes**
- The 'role' field **must** be '"user"', or the request will be rejected.
- If any required field is missing, the API will return a '400 BAD REQUEST' response.
- Passwords should be securely stored using hashing mechanisms.


# 8. API Endpoint: Register a New Admin User

## **Endpoint Details**
- **URL:** '/add_admin_user'
- **Method:** 'POST'
- **Authentication:** Not required
- **Description:** Creates a new admin user account in the system.

## **Request Body (JSON)**
- 'user_id' (integer, required): Unique identifier for the user.
- 'user_name' (string, required): Username for login.
- 'user_full_name' (string, required): Full name of the user.
- 'user_phone_num' (string, required): Contact phone number.
- 'address' (string, required): User's physical address.
- 'email' (string, required): Email address for communication.
- 'password' (string, required): Secure password for authentication.
- 'role' (string, required): Must be set to '"admin"'.

## **Response Details**
- **200 OK**: If the admin user was successfully created.
- **400 BAD REQUEST**: If any required field is missing or if 'role' is not '"admin"'.

## **Example API Request**
```json
{
    "user_id": 1,
    "user_name": "admin_user",
    "user_full_name": "Admin User",
    "user_phone_num": "0523456789",
    "address": "456 Admin St, Tel Aviv",
    "email": "admin@example.com",
    "password": "SecureAdminPass123",
    "role": "admin"
}
```

## **Example API Response (Successful Registration)**
```json
{}
```

## **Example API Response (Missing Fields or Invalid Role)**
```json
{
    "success": false,
    "message": "Either one or more required fields are missing, or 'role' is not set to 'admin'."
}
```

## **Notes**
- The 'role' field **must** be '"admin"', or the request will be rejected.
- If any required field is missing, the API will return a '400 BAD REQUEST' response.
- Passwords should be securely stored using hashing mechanisms.


# 9. API Endpoint: Update User Information

## **Endpoint Details**
- **URL:** '/update_user'
- **Method:** 'POST'
- **Authentication:** Required (User must be logged in)
- **Description:** Updates specific details of a user account.

## **Request Body (JSON)**
- 'user_name' (string, optional): New username.
- 'user_full_name' (string, optional): Updated full name.
- 'user_phone_num' (string, optional): Updated phone number.
- 'address' (string, optional): Updated user address.
- 'email' (string, optional): Updated email address.
- 'password' (string, optional): Updated password.

## **Response Details**
- Returns an empty JSON response ('{}') upon successful update.

## **Example API Request**
```json
{
    "user_name": "updated_noam",
    "email": "updated_email@example.com",
    "address": "789 Updated St, Tel Aviv",
    "password": "NewSecurePass123"
}
```

## **Example API Response (Successful Update)**
```json
{}
```

## **Notes**
- This endpoint **requires authentication**.
- Only fields that are provided in the request will be updated.
- If no valid fields are provided, the request will have no effect.
- The request must be sent with a **valid JSON payload**.
- Password updates should be securely handled and stored using hashing.


# 10. API Endpoint: User Login

## **Endpoint Details**
- **URL:** '/login'
- **Method:** 'POST'
- **Authentication:** Not required
- **Description:** Authenticates a user and returns a session upon successful login.

## **Request Body (JSON)**
- 'user_name' (string, required): The username of the user.
- 'password' (string, required): The password for authentication.

## **Response Details**
- **200 OK**: If login is successful.
- **400 BAD REQUEST**: If the request payload is invalid or missing required fields.
- **401 UNAUTHORIZED**: If authentication fails (wrong username or password).

## **Example API Request**
```json
{
    "user_name": "noam",
    "password": "SecurePass123"
}
```

## **Example API Response (Successful Login)**
```json
""
```

## **Example API Response (Invalid Credentials)**
```json
{
    "error": "Unauthorized"
}
```

## **Example API Response (Missing Fields)**
```json
{
    "error": "Bad Request"
}
```

## **Notes**
- The request **must** be in valid JSON format.
- If 'user_name' or 'password' is missing, the request will return '400 BAD REQUEST'.
- If authentication fails due to incorrect credentials, the request will return '401 UNAUTHORIZED'.
- Upon successful login, a session is created for the user.


# 11. API Endpoint: User Logout

## **Endpoint Details**
- **URL:** '/logout'
- **Method:** 'POST'
- **Authentication:** Required (User must be logged in)
- **Description:** Logs out the current authenticated user by ending the session.

## **Request Body**
- No request body is required.

## **Response Details**
- **200 OK**: If logout is successful.

## **Example API Request**
```
POST /logout
```

## **Example API Response (Successful Logout)**
```json
""
```

## **Notes**
- This endpoint **requires authentication**.
- The request must be made while the user is logged in.
- After logging out, the session is cleared, and the user must log in again to access protected endpoints.


# 12. API Endpoint: Retrieve Cart Items

## **Endpoint Details**
- **URL:** '/carts'
- **Method:** 'GET'
- **Authentication:** Required (User must be logged in)
- **Description:** Retrieves the shopping cart items for a specific user. Can filter by 'model_num'.

## **Query Parameters**
- 'user_id' (integer, required): Retrieve cart items for the specified user.
- 'model_num' (string, optional): Retrieve specific items by their model number.

## **Response Details**
- Returns a JSON object containing cart items and the total cart price.
- **400 BAD REQUEST**: If 'user_id' is missing from the request.

## **Notes**
- This endpoint **requires authentication**.
- If 'user_id' is not provided, the request will be rejected with '400 BAD REQUEST'.
- If 'model_num' is specified, only the matching item will be returned.
- The request must be properly formatted in **JSON**.


# 13. API Endpoint: Retrieve All Cart Items (Admin Only)

## **Endpoint Details**
- **URL:** '/admin/carts'
- **Method:** 'GET'
- **Authentication:** Required (Admin Only)
- **Description:** Retrieves all shopping cart items across all users.

## **Response Details**
- Returns a JSON object containing all users' cart items.
- **403 FORBIDDEN**: If the request is made by a non-admin user.

## **Example API Request**
```
GET /admin/carts
```

## **Example API Response (Successful Request)**
```json
{
    "carts": {
        "123": [
            {
                "model_num": "SOFA-456",
                "name": "Luxury Sofa",
                "quantity": 2,
                "price_per_unit": 1500.00,
                "total_price": 3000.00
            }
        ],
        "456": [
            {
                "model_num": "TABLE-789",
                "name": "Dining Table",
                "quantity": 1,
                "price_per_unit": 1200.00,
                "total_price": 1200.00
            },
            {
                "model_num": "CHAIR-999",
                "name": "Office Chair",
                "quantity": 3,
                "price_per_unit": 450.00,
                "total_price": 1350.00
            }
        ]
    }
}
```

## **Example API Response (Unauthorized Request)**
```json
{
    "error": "Forbidden",
    "message": "Admin privileges required."
}
```

## **Notes**
- This endpoint **requires Admin privileges**.
- The request will be rejected with '403 FORBIDDEN' if made by a non-admin user.
- Returns all active cart items across all users in the system.


# 14. API Endpoint: Add Item to Cart

## **Endpoint Details**
- **URL:** '/user/add_item_to_cart'
- **Method:** 'POST'
- **Authentication:** Required (User must be logged in)
- **Description:** Adds a new item to the user's shopping cart.

## **Request Body (JSON)**
- 'user_id' (integer, required): The ID of the user adding the item.
- 'model_num' (string, required): The unique identifier of the item.
- 'quantity' (integer, required): The quantity of the item to be added.

## **Response Details**
- Returns an empty JSON response ('{}') upon successful addition.

## **Example API Request**
```json
{
    "user_id": 123,
    "model_num": "CHAIR-001",
    "quantity": 2
}
```

## **Example API Response (Successful Addition)**
```json
{}
```

## **Notes**
- This endpoint **requires authentication**.
- The request must be sent in **valid JSON format**.
- If the 'model_num' does not exist, the request will not be processed.
- The user must have a valid session to add items to the cart.


# 15. API Endpoint: Update Item Quantity in Cart

## **Endpoint Details**
- **URL:** '/user/update_cart_item_quantity'
- **Method:** 'POST'
- **Authentication:** Required (User must be logged in)
- **Description:** Updates the quantity of an item in the user's shopping cart.

## **Request Body (JSON)**
- 'user_id' (integer, required): The ID of the user updating the cart.
- 'model_num' (string, required): The unique identifier of the item to update.
- 'quantity' (integer, required): The new quantity of the item.

## **Response Details**
- Returns an empty JSON response ('{}') upon successful update.

## **Example API Request**
```json
{
    "user_id": 123,
    "model_num": "CHAIR-001",
    "quantity": 3
}
```

## **Example API Response (Successful Update)**
```json
{}
```

## **Notes**
- This endpoint **requires authentication**.
- The request must be sent in **valid JSON format**.
- If the 'model_num' does not exist in the cart, the request will not update any item.
- The user must have a valid session to update cart items.


# 16. API Endpoint: Delete Item from Cart

## **Endpoint Details**
- **URL:** '/user/delete_cart_item'
- **Method:** 'POST'
- **Authentication:** Required (User must be logged in)
- **Description:** Removes an item from the user's shopping cart.

## **Request Body (JSON)**
- 'user_id' (integer, required): The ID of the user removing the item.
- 'model_num' (string, required): The unique identifier of the item to be removed.

## **Response Details**
- Returns an empty JSON response ('{}') upon successful deletion.

## **Example API Request**
```json
{
    "user_id": 123,
    "model_num": "CHAIR-001"
}
```

## **Example API Response (Successful Deletion)**
```json
{}
```

## **Notes**
- This endpoint **requires authentication**.
- The request must be sent in **valid JSON format**.
- If the 'model_num' does not exist in the cart, the request will not delete any item.
- The user must have a valid session to remove items from the cart.


# 17. API Endpoint: Retrieve User Orders

## **Endpoint Details**
- **URL:** '/user/orders/<user_id>'
- **Method:** 'GET'
- **Authentication:** Required (User must be logged in)
- **Description:** Retrieves a list of orders for a specific user. Can filter by 'order_num'.

## **Path Parameters**
- 'user_id' (integer, required): The ID of the user whose orders are being retrieved.

## **Query Parameters (Optional)**
- 'order_num' (integer): Retrieve a specific order by its number.

## **Response Details**
- Returns a JSON object containing the user's order history.

## **Notes**
- This endpoint **requires authentication**.
- If 'order_num' is specified, only that order will be returned.
- Orders are returned in descending order by creation time.
- The request must be properly formatted.


# 18. API Endpoint: Retrieve All Orders (Admin Only)

## **Endpoint Details**
- **URL:** /admin/orders'
- **Method:** 'GET'
- **Authentication:** Required (Admin Only)
- **Description:** Retrieves all orders in the system. Can filter by 'user_id' or 'order_num'.

## **Query Parameters (Optional)**
- 'user_id' (integer): Retrieve orders for a specific user.
- 'order_num' (integer): Retrieve a specific order by its number.

## **Response Details**
- Returns a JSON object containing all orders in the system.

## **Notes**
- This endpoint **requires Admin privileges**.
- If 'user_id' is specified, only orders from that user will be returned.
- If 'order_num' is specified, only that order will be returned.
- Orders are returned in descending order by creation time.
- The request must be properly formatted.


# 19. API Endpoint: Update Order Status (Admin Only)

## **Endpoint Details**
- **URL:** '/admin/update_order_status'
- **Method:** 'POST'
- **Authentication:** Required (Admin Only)
- **Description:** Updates the status of an existing order.

## **Request Body (JSON)**
- 'order_num' (integer, required): The unique identifier of the order to update.
- 'status' (string, required): The new status of the order (e.g., "Pending", "Shipped", "Delivered").

## **Response Details**
- Returns an empty JSON response ('{}') upon successful update.
- **400 BAD REQUEST**: If required fields are missing.

## **Example API Request**
```json
{
    "order_num": 98765,
    "status": "Shipped"
}
```

## **Example API Response (Successful Update)**
```json
{}
```

## **Example API Response (Missing Fields)**
```json
{
    "error": "Bad Request",
    "message": "new order status is missing"
}
```

```json
{
    "error": "Bad Request",
    "message": "order num is missing"
}
```

## **Notes**
- This endpoint **requires Admin privileges**.
- The request must be sent in **valid JSON format**.
- If the 'order_num' does not exist, the request will not update any order.
- The provided 'status' should be a valid predefined order status.


# 20. API Endpoint: Process Checkout

## **Endpoint Details**
- **URL:** '/checkout'
- **Method:** 'POST'
- **Authentication:** Required (User must be logged in)
- **Description:** Processes the checkout by finalizing the cart, processing the payment, and creating an order.

## **Request Body (JSON)**
- 'user_id' (integer, required): The ID of the user checking out.
- 'address' (string, required): The shipping address for the order.
- 'payment_method' (string, required): The payment method to be used (e.g., "credit_card", "paypal").

## **Response Details**
- Returns a JSON object containing the checkout result.
- **400 BAD REQUEST**: If required fields are missing or invalid.
- **400 BAD REQUEST**: If the payment method is invalid.

## **Example API Request**
```json
{
    "user_id": 123,
    "address": "123 Main St, Tel Aviv",
    "payment_method": "credit_card"
}
```

## **Example API Response (Successful Checkout)**
```json
{
    "status": "success",
    "message": "Order placed successfully",
    "order_id": 98765
}
```

## **Example API Response (Missing Fields)**
```json
{
    "status": "error",
    "message": "Missing required fields"
}
```

## **Example API Response (Invalid Payment Method)**
```json
{
    "error": "Invalid payment method"
}
```

## **Notes**
- This endpoint **requires authentication**.
- The request must be sent in **valid JSON format**.
- If 'payment_method' is invalid, the request will return an error.
- Upon success, an order is created, and the payment is processed.
---

## Warning Summary  - Online Furniture Store

During testing, we encountered deprecation warnings related to **SQLAlchemy 2.0**:  

- `declarative_base()` should now be used as `sqlalchemy.orm.declarative_base()`.  
- `Query.get()` is considered legacy and should be replaced with `Session.get()`.  

These warnings appear because our implementation was based on an older SQLAlchemy version. However, since this is a **course project** that won’t be maintained after the semester, we chose not to refactor. The current implementation remains functional, and if extended in the future, updating these methods would ensure long-term compatibility.

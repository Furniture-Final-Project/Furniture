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







---

## Warning Summary  - Online Furniture Store

During testing, we encountered deprecation warnings related to **SQLAlchemy 2.0**:  

- `declarative_base()` should now be used as `sqlalchemy.orm.declarative_base()`.  
- `Query.get()` is considered legacy and should be replaced with `Session.get()`.  

These warnings appear because our implementation was based on an older SQLAlchemy version. However, since this is a **course project** that won’t be maintained after the semester, we chose not to refactor. The current implementation remains functional, and if extended in the future, updating these methods would ensure long-term compatibility.

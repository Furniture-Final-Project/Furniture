# furniture - the furniture store

## Root Convention

All commands are [assumed to run from the root of the project] - the directory in which _this README_ is located.

## Installation

    $ pip install -r requirements.txt

## Running pre-commit


    $ pre-commit run --all-files

## List of all Endpoints

    '/items'                            methods=['GET']
    '/admin/add_item'                   methods=['POST']
    '/admin/update_item'                methods=['POST']
    '/admin/delete_item'                methods=['POST']
    '/admin/users'                      methods=['GET']
    '/add_user'                         methods=['POST']
    '/add_admin_user'                   methods=['POST']
    '/update_user'                      methods=['POST']
    '/login'                            methods=['POST']
    '/logout'                           methods=['POST']
    '/carts'                            methods=['GET']
    '/admin/carts'                      methods=['GET']
    '/user/add_item_to_cart'            methods=['POST']
    '/user/update_cart_item_quantity'   methods=['POST']
    '/user/delete_cart_item'            methods=['POST']
    '/user/orders/<user_id>'            methods=['GET']
    '/admin/orders'                     methods=['GET']
    '/admin/update_order_status'        methods=['POST']
    '/checkout'                         methods=['POST']

# NomiNomi
## Order Management App

NomiNomi is an order management application built with Flask. It allows you to manage orders, track their progress, and view analytics. This README.md provides a brief overview of the project.

## Prerequisites

* Docker
* Docker-Compose


## Usage
Once the application is running, you can use NomiNomi to perform the following actions:

- View the home page by visiting the root URL (http://localhost:5000).
- Add a new order by visiting /add_new_order and filling out the order form.
- Remove an order by visiting /remove_order and providing the phone number associated with the order.
- Update an existing order by visiting /update_order and filling out the order form with the updated details.
- View all orders by visiting /view_all_orders.
- View undelivered orders by visiting /view_all_orders_undelivered.
- View analytics and revenue by visiting /view_analytics.


## Installation

switch directory to the app, and run docker compose.

```sh
cd orders_management_app
docker compose up
```


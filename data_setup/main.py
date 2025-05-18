import requests
import os
import csv
import json
import io
import faker

INGRESS_URL = os.getenv("INGRESS_URL", "http://localhost:80")

USERS_BACKEND_URL = f"{INGRESS_URL}/api/v1/users"

SUPPLIERS_BACKEND_URL = f"{INGRESS_URL}/suppliers"

INVENTORY_BACKEND_URL = f"{INGRESS_URL}/inventory"

LOGISTICS_BACKEND_URL = f"{INGRESS_URL}/logistic"

SALES_BACKEND_URL = f"{INGRESS_URL}/api/v1/sales"

PRODUCTS_FILE = os.getenv("PRODUCTS_FILE", "better_manufacturer_product_names.csv")

fake = faker.Faker()
faker.Faker.seed(0)


def do_request(method, url, params=None, data=None, auth_token=None):
    headers = {
        "Content-Type": "application/json",
    }
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    response = requests.request(method, url, params=params, json=data, headers=headers)
    if response.ok:
        return response.json()
    else:
        print(f"Error: {url} {response.status_code} - {response.text}")
        assert False


def do_post_request(url, data, auth_token=None):
    return do_request("POST", url, data=data, auth_token=auth_token)


def do_get_request(url, params=None, auth_token=None):
    return do_request("GET", url, params=params, auth_token=auth_token)


def post_request_csv(url, files=None, data=None, auth_token=None):
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    response = requests.post(url, files=files, headers=headers, data=data)
    if response.ok:
        return response.json()
    else:
        print(f"Error: {url} {response.status_code} - {response.text}")
        assert False


def reset_all_data():
    print("Resetting all data...")
    # reset users
    do_post_request(f"{USERS_BACKEND_URL}/reset-db", {})
    # reset suppliers
    do_post_request(f"{SUPPLIERS_BACKEND_URL}/reset-db", {})
    # reset inventory
    do_post_request(f"{INVENTORY_BACKEND_URL}/reset", {})
    # reset logistics
    do_post_request(f"{LOGISTICS_BACKEND_URL}/reset", {})
    # reset sales
    do_post_request(f"{SALES_BACKEND_URL}/reset-db", {})
    print("All data reset.")


def auth_user(username, password):
    # login user
    response = do_post_request(
        f"{USERS_BACKEND_URL}/login",
        {"username": username, "password": password},
    )
    return response["access_token"], response["user"]["id"]


def load_manufacturers(seller_token, products) -> list:
    print("Loading manufacturers...")
    index = 0
    manufacturer_ids = []
    with open("manufacturers.json", "r") as manufacturers_file:
        # load products
        manufacturers = json.load(manufacturers_file)
        for manufacture in manufacturers:
            response = do_post_request(
                f"{SUPPLIERS_BACKEND_URL}/manufacturers",
                manufacture,
                auth_token=seller_token,
            )
            id = response["id"]
            manufacturer_ids.append(id)
            output = io.StringIO()
            batch_file = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
            batch_file.writerow(["name", "product_code", "price", "images"])
            for _ in range(10):
                batch_file.writerow(products[index])
                index += 1
            output.seek(0)
            post_request_csv(
                f"{SUPPLIERS_BACKEND_URL}/manufacturers/{id}/products/batch/",
                {"file": output},
                auth_token=seller_token,
            )

    print("manufacturers loaded.")
    return manufacturer_ids


def create_warehouses(seller_token) -> list[str]:
    print("Creating warehouse...")
    ids = []
    with open("warehouses.json", "r") as warehouses_file:
        warehouses = json.load(warehouses_file)
        for warehouse in warehouses:
            response = do_post_request(
                f"{INVENTORY_BACKEND_URL}/warehouse",
                warehouse,
                auth_token=seller_token,
            )
            # print the response
            id = response["warehouse_id"]
            ids.append(id)
    print("Warehouses created")
    return ids


def load_inventory(seller_token, warehouse_ids, products):
    print("Loading inventory...")

    products_per_warehouse = len(products) // len(warehouse_ids)

    for i, warehouse_id in enumerate(warehouse_ids):
        # Select some random products
        if i == 0:
            selected_products = products
        else:
            selected_products = fake.random_choices(
                elements=products, length=products_per_warehouse
            )
        output = io.StringIO()
        batch_file = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        batch_file.writerow(["product_code", "quantity"])
        for product in selected_products:
            batch_file.writerow([product[1], fake.random_int(50, 100)])
        # Save output to a file
        if i == 0:
            with open(f"inventory_{warehouse_id}.csv", "w") as f:
                output.seek(0)
                f.write(output.getvalue())
        output.seek(0)
        post_request_csv(
            f"{INVENTORY_BACKEND_URL}/stock/csv",
            files={"inventory_upload": ("inventory.csv", output, "text/csv")},
            data={"warehouse_id": warehouse_id},
            auth_token=seller_token,
        )
    print("Inventory loaded.")


def load_sellers(seller_token):
    print("Loading sellers...")
    seller_ids = []
    with open("sellers.json", "r") as sellers_file:
        # load products
        sellers = json.load(sellers_file)
        for seller in sellers:
            response = do_post_request(
                f"{USERS_BACKEND_URL}/sellers/",
                seller,
                auth_token=seller_token,
            )
            id = response["id"]
            seller_ids.append(id)

    print("Sellers loaded.")
    return seller_ids


def get_all_product_ids(seller_token):
    print("Getting all product ids...")
    response = do_post_request(
        f"{SUPPLIERS_BACKEND_URL}/manufacturers/listProducts/",
        {},
        auth_token=seller_token,
    )
    product_ids = [product["id"] for product in response]
    print("Product ids loaded.")
    return product_ids


def get_all_seller_ids(staff_token):
    print("Getting all seller ids...")
    response = do_get_request(
        f"{USERS_BACKEND_URL}/sellers/",
        auth_token=staff_token,
    )
    seller_ids = [seller["id"] for seller in response]
    print("Seller ids loaded.")
    return seller_ids


def create_plans_for_sellers(seller_token, product_ids, seller_ids, main_seller_id):

    for product_id in product_ids:
        selected_ids = list(
            fake.random_choices(elements=seller_ids, length=fake.random_int(1, 5))
        )
        selected_ids.append(main_seller_id)
        selected_ids = list(set(selected_ids))
        plan = {
            "product_id": product_id,
            "goal": fake.random_int(1, 100),
            "start_date": fake.date_between(
                start_date="today", end_date="+1y"
            ).strftime("%Y-%m-%d"),
            "end_date": fake.date_between(start_date="+1y", end_date="+2y").strftime(
                "%Y-%m-%d"
            ),
            "seller_ids": selected_ids,
        }
        do_post_request(
            f"{SALES_BACKEND_URL}/plans/",
            plan,
            auth_token=seller_token,
        )


def registrar_clientes(clients):
    print("Creating clients...")
    client_ids = []
    for client in clients:
        response = do_post_request(
            f"{USERS_BACKEND_URL}/clients/",
            client,
        )
        id = response["id"]
        client_ids.append(id)

    print("Clients created.")
    return client_ids


def get_seller_clients(seller_token):
    print("Getting clients for seller...")
    response = do_get_request(
        f"{SALES_BACKEND_URL}/sellers/clients/",
        auth_token=seller_token,
    )
    client_ids = [client["client"]["id"] for client in response]
    print("Clients loaded.")
    return client_ids


def get_seller_routes(seller_token):
    print("Getting routes for seller...")
    response = do_get_request(
        f"{SALES_BACKEND_URL}/routes/",
        auth_token=seller_token,
    )
    route_ids = [route["id"] for route in response]
    print("Routes loaded.")
    return route_ids


def create_sale(auth_token, product_ids, client_id=None):
    print("Creating sale...")
    sale = {
        "items": [
            {
                "product_id": p,
                "quantity": fake.random_int(2, 5),
            }
            for p in fake.random_choices(
                elements=product_ids, length=fake.random_int(2, 5)
            )
        ],
    }
    if client_id:
        sale["client_id"] = client_id
    response = do_post_request(
        f"{SALES_BACKEND_URL}/sales/",
        sale,
        auth_token=auth_token,
    )
    print("Sale created.")
    return response


def get_sales(auth_token):
    print("Getting sales...")
    response = do_get_request(
        f"{SALES_BACKEND_URL}/sales/",
        auth_token=auth_token,
    )
    print("Sales loaded.")
    return response


def export_sales(auth_token):
    print("Exporting sales...")
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    response = requests.get(
        f"{SALES_BACKEND_URL}/sales/export/",
        headers=headers,
    )
    if not response.ok:
        print(f"Error: {response.status_code} - {response.text}")
        assert False
    print("Sales exported.")
    return response


def create_deliveries(staff_token, warehouse_ids):
    print("Creating deliveries...")
    for warehouse_id in warehouse_ids:
        delivery = {
            "warehouse_id": warehouse_id,
            "delivery_date": fake.date_between(
                start_date="+1d", end_date="+13d"
            ).strftime("%Y-%m-%d"),
        }
        do_post_request(
            f"{LOGISTICS_BACKEND_URL}/delivery/",
            delivery,
            auth_token=staff_token,
        )
    print("Deliveries created.")


def list_warehouses(staff_token):
    print("Listing warehouses...")
    response = do_get_request(
        f"{INVENTORY_BACKEND_URL}/warehouse",
        auth_token=staff_token,
    )
    warehouse_ids = [warehouse["warehouse_id"] for warehouse in response]
    print("Warehouses loaded.")
    return warehouse_ids


if __name__ == "__main__":
    # build some data that makes sense
    with open(PRODUCTS_FILE, "r") as products_file, open(
        "clients.json", "r"
    ) as clients_file:
        reader = csv.reader(products_file)
        # skip the header
        next(reader)
        products = list(reader)
        clients = json.load(clients_file)

    reset_all_data()
    staff_token, staff_user_id = auth_user("staff_user", "staff_user_password")
    seller_token, seller_user_id = auth_user("seller_user", "seller_user_password")
    client_token, client_user_id = auth_user("client_user", "client_user_password")
    manufacturers = load_manufacturers(staff_token, products)
    seeded_warehouse_ids = list_warehouses(staff_token)
    warehouses = create_warehouses(staff_token)
    load_inventory(staff_token, seeded_warehouse_ids, products)
    load_sellers(staff_token)
    product_ids = get_all_product_ids(staff_token)
    seller_ids = get_all_seller_ids(staff_token)
    create_plans_for_sellers(staff_token, product_ids, seller_ids, seller_user_id)
    new_client_ids = registrar_clientes(clients)
    seller_clients = get_seller_clients(seller_token)
    get_seller_routes(seller_token)
    create_sale(seller_token, product_ids, seller_clients[0])
    create_sale(seller_token, product_ids, seller_clients[1])
    get_sales(seller_token)
    create_sale(client_token, product_ids)
    get_sales(client_token)
    get_sales(staff_token)
    create_deliveries(staff_token, warehouses)
    export_sales(staff_token)

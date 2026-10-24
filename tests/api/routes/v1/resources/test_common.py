import pytest
from fastapi.testclient import TestClient

ENTITY_CASES = [
    {
        "name": "categories",
        "base": "/v1/categories",
        "id_value": 1,
        "payload": {
            "categoryId": 1,
            "categoryName": "Beverages",
            "description": "Soft drinks",
            "picture": None,
        },
    },
    {
        "name": "customers",
        "base": "/v1/customers",
        "id_value": "ALFKI",
        "payload": {
            "customerId": "ALFKI",
            "companyName": "Alfreds Futterkiste",
            "contactName": "Maria Anders",
            "contactTitle": "Sales Representative",
            "address": "Obere Str. 57",
            "city": "Berlin",
            "region": None,
            "postalCode": "12209",
            "country": "Germany",
            "phone": "030-0074321",
            "fax": "030-0076545",
        },
    },
    {
        "name": "employees",
        "base": "/v1/employees",
        "id_value": 1,
        "payload": {
            "employeeId": 1,
            "lastName": "Davolio",
            "firstName": "Nancy",
            "title": "Sales Representative",
            "titleOfCourtesy": "Ms.",
            "birthDate": None,
            "hireDate": None,
            "address": "507 - 20th Ave. E.",
            "city": "Seattle",
            "region": "WA",
            "postalCode": "98122",
            "country": "USA",
            "homePhone": "(206) 555-9857",
            "extension": "5467",
            "photo": None,
            "notes": None,
            "reportsTo": None,
            "photoPath": None,
        },
    },
    {
        "name": "orders",
        "base": "/v1/orders",
        "id_value": 1001,
        "payload": {
            "orderId": 1001,
            "customerId": "ALFKI",
            "employeeId": 1,
            "orderDate": None,
            "requiredDate": None,
            "shippedDate": None,
            "shipVia": None,
            "freight": None,
            "shipName": "Ship Name",
            "shipAddress": "Ship Address",
            "shipCity": "Ship City",
            "shipRegion": None,
            "shipPostalCode": "00000",
            "shipCountry": "USA",
        },
    },
    {
        "name": "products",
        "base": "/v1/products",
        "id_value": 1,
        "payload": {
            "productId": 1,
            "productName": "Chai",
            "supplierId": None,
            "categoryId": None,
            "quantityPerUnit": "10 boxes",
            "unitPrice": 18.0,
            "unitsInStock": 39,
            "unitsOnOrder": 0,
            "reorderLevel": 10,
            "discontinued": False,
        },
    },
    {
        "name": "shippers",
        "base": "/v1/shippers",
        "id_value": 1,
        "payload": {
            "shipperId": 1,
            "companyName": "Speedy Express",
            "phone": "(503) 555-9831",
        },
    },
    {
        "name": "suppliers",
        "base": "/v1/suppliers",
        "id_value": 1,
        "payload": {
            "supplierId": 1,
            "companyName": "Exotic Liquids",
            "contactName": "Charlotte Cooper",
            "contactTitle": "Purchasing Manager",
            "address": "49 Gilbert St.",
            "city": "London",
            "region": None,
            "postalCode": "EC1 4SD",
            "country": "UK",
            "phone": "(171) 555-2222",
            "fax": None,
            "homePage": None,
        },
    },
]


@pytest.mark.parametrize("case", ENTITY_CASES, ids=[case["name"] for case in ENTITY_CASES])
def test_single_key_domain_crud_contract(client: TestClient, case: dict) -> None:
    add_response = client.post(
        f"{case['base']}/add", json=case["payload"], headers={"X-Api-Version": "1"}
    )
    assert add_response.status_code == 201
    assert "id" in add_response.json()
    assert add_response.json()["id"] == case["id_value"]

    get_all_response = client.get(f"{case['base']}/get-all", headers={"X-Api-Version": "1"})
    assert get_all_response.status_code == 200
    assert isinstance(get_all_response.json(), list)

    get_response = client.get(
        f"{case['base']}/get/{case['id_value']}",
        headers={"X-Api-Version": "1"},
    )
    assert get_response.status_code == 200

    update_response = client.put(
        f"{case['base']}/update", json=case["payload"], headers={"X-Api-Version": "1"}
    )
    assert update_response.status_code == 204

    delete_response = client.delete(
        f"{case['base']}/delete/{case['id_value']}",
        headers={"X-Api-Version": "1"},
    )
    assert delete_response.status_code == 204


def test_identity_key_is_generated_when_category_add_omits_key(client: TestClient) -> None:
    payload = {
        "categoryName": "Test Cat",
        "description": "Test Category",
        "picture": None,
    }

    response = client.post("/v1/categories/add", json=payload, headers={"X-Api-Version": "1"})

    assert response.status_code == 201
    assert response.json()["id"] > 0


def test_customer_add_returns_string_id(client: TestClient) -> None:
    payload = {"customerId": "XYZPD", "companyName": "Test Company"}

    response = client.post("/v1/customers/add", json=payload, headers={"X-Api-Version": "1"})

    assert response.status_code == 201
    assert response.json() == {"id": "XYZPD"}


@pytest.mark.parametrize("operation", ["get", "delete"])
def test_non_numeric_id_for_int_key_is_a_bad_request(client: TestClient, operation: str) -> None:
    send = getattr(client, operation)

    response = send(f"/v1/categories/{operation}/abc", headers={"X-Api-Version": "1"})

    assert response.status_code == 400
    body = response.json()
    assert body["title"] == "Bad Request"
    assert body["detail"].startswith("path.categoryId: ")


@pytest.mark.parametrize(
    ("path", "query", "field"),
    [
        ("/v1/categories/get-all", "page=-1", "query.page: "),
        ("/v1/categories/get-all", "pageSize=0", "query.pageSize: "),
        ("/v1/order-details/get-all", "page=-1", "query.page: "),
        ("/v1/order-details/get-all", "pageSize=0", "query.pageSize: "),
    ],
)
def test_get_all_out_of_range_paging_is_a_bad_request(
    client: TestClient, path: str, query: str, field: str
) -> None:
    response = client.get(f"{path}?{query}", headers={"X-Api-Version": "1"})

    assert response.status_code == 400
    assert response.json()["detail"].startswith(field)


def test_get_all_lowest_valid_paging_is_accepted(client: TestClient) -> None:
    response = client.get(
        "/v1/categories/get-all?page=0&pageSize=1", headers={"X-Api-Version": "1"}
    )

    assert response.status_code == 200


def test_customer_add_requires_customer_id(client: TestClient) -> None:
    invalid_payload = {"companyName": "Missing customerId"}
    response = client.post(
        "/v1/customers/add", json=invalid_payload, headers={"X-Api-Version": "1"}
    )

    assert response.status_code == 400
    body = response.json()
    assert body["title"] == "Bad Request"
    assert body["status"] == 400


def test_legacy_uppercase_id_field_is_rejected(client: TestClient) -> None:
    payload = {"categoryID": 5, "categoryName": "Legacy"}

    response = client.post("/v1/categories/add", json=payload, headers={"X-Api-Version": "1"})

    assert response.status_code == 400
    assert "body.categoryID: " in response.json()["detail"]


def test_get_by_id_returns_camel_case_id_field(client: TestClient) -> None:
    payload = {"categoryId": 7, "categoryName": "Produce"}
    client.post("/v1/categories/add", json=payload, headers={"X-Api-Version": "1"})

    response = client.get("/v1/categories/get/7", headers={"X-Api-Version": "1"})

    assert response.status_code == 200
    assert response.json()["categoryId"] == 7


def test_product_add_defaults_optional_non_nullable_fields(client: TestClient) -> None:
    payload = {"productId": 50, "productName": "Minimal"}

    add_response = client.post("/v1/products/add", json=payload, headers={"X-Api-Version": "1"})
    assert add_response.status_code == 201

    body = client.get("/v1/products/get/50", headers={"X-Api-Version": "1"}).json()
    assert body["discontinued"] is False
    assert body["reorderLevel"] == 0
    assert body["unitsInStock"] == 0
    assert body["unitsOnOrder"] == 0


def test_shipper_add_does_not_require_company_name(client: TestClient) -> None:
    response = client.post(
        "/v1/shippers/add", json={"phone": "(503) 555-0000"}, headers={"X-Api-Version": "1"}
    )

    assert response.status_code == 201
    assert response.json()["id"] > 0


def test_add_accepts_structured_json_media_type(client: TestClient) -> None:
    response = client.post(
        "/v1/categories/add",
        content='{"categoryName": "Vendor JSON"}',
        headers={"X-Api-Version": "1", "Content-Type": "application/vnd.pilot+json"},
    )

    assert response.status_code == 201

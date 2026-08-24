import pytest
from fastapi.testclient import TestClient


ENTITY_CASES = [
    {
        "name": "categories",
        "base": "/categories",
        "id_value": 1,
        "payload": {
            "categoryID": 1,
            "categoryName": "Beverages",
            "description": "Soft drinks",
            "picture": None,
        },
    },
    {
        "name": "customers",
        "base": "/customers",
        "id_value": "ALFKI",
        "payload": {
            "customerID": "ALFKI",
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
        "base": "/employees",
        "id_value": 1,
        "payload": {
            "employeeID": 1,
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
        "base": "/orders",
        "id_value": 1001,
        "payload": {
            "orderID": 1001,
            "customerID": "ALFKI",
            "employeeID": 1,
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
        "base": "/products",
        "id_value": 1,
        "payload": {
            "productID": 1,
            "productName": "Chai",
            "supplierID": None,
            "categoryID": None,
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
        "base": "/shippers",
        "id_value": 1,
        "payload": {
            "shipperID": 1,
            "companyName": "Speedy Express",
            "phone": "(503) 555-9831",
        },
    },
    {
        "name": "suppliers",
        "base": "/suppliers",
        "id_value": 1,
        "payload": {
            "supplierID": 1,
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
    add_response = client.post(f"{case['base']}/add", json=case["payload"], headers={"ApiVersion": "1"})
    assert add_response.status_code == 200
    assert "id" in add_response.json()

    get_all_response = client.get(f"{case['base']}/get-all", headers={"ApiVersion": "1"})
    assert get_all_response.status_code == 200
    assert isinstance(get_all_response.json(), list)

    get_response = client.get(
        f"{case['base']}/get/{case['id_value']}",
        headers={"ApiVersion": "1"},
    )
    assert get_response.status_code == 200

    update_response = client.put(f"{case['base']}/update", json=case["payload"], headers={"ApiVersion": "1"})
    assert update_response.status_code == 204

    delete_response = client.delete(
        f"{case['base']}/delete/{case['id_value']}",
        headers={"ApiVersion": "1"},
    )
    assert delete_response.status_code == 204


def test_identity_key_is_generated_when_category_add_omits_key(client: TestClient) -> None:
    payload = {
        "categoryName": "Test Cat",
        "description": "Test Category",
        "picture": None,
    }

    response = client.post("/categories/add", json=payload, headers={"ApiVersion": "1"})

    assert response.status_code == 200
    assert response.json()["id"] > 0


def test_customer_add_requires_customer_id(client: TestClient) -> None:
    invalid_payload = {"companyName": "Missing customerID"}
    response = client.post("/customers/add", json=invalid_payload, headers={"ApiVersion": "1"})

    assert response.status_code == 400
    body = response.json()
    assert body["title"] == "Bad Request"
    assert body["status"] == 400

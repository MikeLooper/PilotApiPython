from fastapi.testclient import TestClient


def test_order_details_crud_contract(client: TestClient) -> None:
    payload = {
        "orderID": 1001,
        "productID": 1,
        "unitPrice": 10.5,
        "quantity": 2,
        "discount": 0.0,
    }

    add_response = client.post("/v1/order-details/add", json=payload, headers={"ApiVersion": "1"})
    assert add_response.status_code == 200

    get_response = client.get(
        "/v1/order-details/get/product/1/order/1001",
        headers={"ApiVersion": "1"},
    )
    assert get_response.status_code == 200

    update_response = client.put("/v1/order-details/update", json=payload, headers={"ApiVersion": "1"})
    assert update_response.status_code == 204

    delete_response = client.delete(
        "/v1/order-details/delete/product/1/order/1001",
        headers={"ApiVersion": "1"},
    )
    assert delete_response.status_code == 204

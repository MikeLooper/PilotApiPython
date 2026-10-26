import pytest
from fastapi.testclient import TestClient


def test_order_details_crud_contract(client: TestClient) -> None:
    payload = {
        "orderId": 1001,
        "productId": 1,
        "unitPrice": 10.5,
        "quantity": 2,
        "discount": 0.0,
    }

    add_response = client.post(
        "/v1/order-details/add", json=payload, headers={"X-Api-Version": "1"}
    )
    assert add_response.status_code == 201
    assert add_response.json() == {"orderId": 1001, "productId": 1}

    get_response = client.get(
        "/v1/order-details/get/product/1/order/1001",
        headers={"X-Api-Version": "1"},
    )
    assert get_response.status_code == 200

    update_response = client.put(
        "/v1/order-details/update", json=payload, headers={"X-Api-Version": "1"}
    )
    assert update_response.status_code == 204

    delete_response = client.delete(
        "/v1/order-details/delete/product/1/order/1001",
        headers={"X-Api-Version": "1"},
    )
    assert delete_response.status_code == 204


@pytest.mark.parametrize(
    ("path", "field"),
    [
        ("/v1/order-details/get/product/0/order/1001", "path.productId: "),
        ("/v1/order-details/get/product/1/order/2147483648", "path.orderId: "),
        ("/v1/order-details/delete/product/1/order/0", "path.orderId: "),
    ],
)
def test_order_detail_out_of_range_key_is_a_bad_request(
    client: TestClient, path: str, field: str
) -> None:
    send = client.get if "/get/" in path else client.delete

    response = send(path, headers={"X-Api-Version": "1"})

    assert response.status_code == 400
    assert response.json()["detail"].startswith(field)


def test_order_detail_add_with_discount_over_one_is_a_bad_request(client: TestClient) -> None:
    payload = {"orderId": 1001, "productId": 1, "unitPrice": 10.5, "quantity": 2, "discount": 1.5}

    response = client.post("/v1/order-details/add", json=payload, headers={"X-Api-Version": "1"})

    assert response.status_code == 400
    assert "body.discount: " in response.json()["detail"]

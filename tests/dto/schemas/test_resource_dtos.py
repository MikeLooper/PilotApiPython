import pytest
from pydantic import BaseModel, ValidationError

from pilot_api.dto.schemas import (
    CategoriesDto,
    CustomersDto,
    EmployeesDto,
    OrderDetailsDto,
    OrdersDto,
    ProductsDto,
    ShippersDto,
    SuppliersDto,
)

# The smallest payload each DTO accepts.
MINIMAL_PAYLOADS: dict[type[BaseModel], dict] = {
    CategoriesDto: {"categoryName": "Beverages"},
    CustomersDto: {"customerId": "ALFKI", "companyName": "Alfreds Futterkiste"},
    EmployeesDto: {"firstName": "Nancy", "lastName": "Davolio"},
    OrderDetailsDto: {
        "orderId": 10248,
        "productId": 11,
        "unitPrice": 14.0,
        "quantity": 12,
        "discount": 0,
    },
    OrdersDto: {},
    ProductsDto: {"productName": "Chai"},
    ShippersDto: {"companyName": "Speedy Express"},
    SuppliersDto: {"companyName": "Exotic Liquids"},
}

# (DTO, field, longest accepted length) for every length-bounded string property.
MAX_LENGTHS = [
    (CategoriesDto, "categoryName", 15),
    (CustomersDto, "address", 60),
    (CustomersDto, "city", 15),
    (CustomersDto, "companyName", 40),
    (CustomersDto, "contactName", 30),
    (CustomersDto, "contactTitle", 30),
    (CustomersDto, "country", 15),
    (CustomersDto, "fax", 24),
    (CustomersDto, "phone", 24),
    (CustomersDto, "postalCode", 10),
    (CustomersDto, "region", 15),
    (EmployeesDto, "address", 60),
    (EmployeesDto, "city", 15),
    (EmployeesDto, "country", 15),
    (EmployeesDto, "extension", 4),
    (EmployeesDto, "firstName", 10),
    (EmployeesDto, "homePhone", 24),
    (EmployeesDto, "lastName", 20),
    (EmployeesDto, "photoPath", 255),
    (EmployeesDto, "postalCode", 10),
    (EmployeesDto, "region", 15),
    (EmployeesDto, "title", 30),
    (EmployeesDto, "titleOfCourtesy", 25),
    (OrdersDto, "shipAddress", 60),
    (OrdersDto, "shipCity", 15),
    (OrdersDto, "shipCountry", 15),
    (OrdersDto, "shipName", 40),
    (OrdersDto, "shipPostalCode", 10),
    (OrdersDto, "shipRegion", 15),
    (ProductsDto, "productName", 40),
    (ProductsDto, "quantityPerUnit", 20),
    (ShippersDto, "companyName", 40),
    (ShippersDto, "phone", 24),
    (SuppliersDto, "address", 60),
    (SuppliersDto, "city", 15),
    (SuppliersDto, "companyName", 40),
    (SuppliersDto, "contactName", 30),
    (SuppliersDto, "contactTitle", 30),
    (SuppliersDto, "country", 15),
    (SuppliersDto, "fax", 24),
    (SuppliersDto, "phone", 24),
    (SuppliersDto, "postalCode", 10),
    (SuppliersDto, "region", 15),
]

# Required string properties the definition declares non-null with a minimum length of 1.
REQUIRED_TEXT = [
    (CategoriesDto, "categoryName"),
    (CustomersDto, "companyName"),
    (EmployeesDto, "firstName"),
    (EmployeesDto, "lastName"),
    (ProductsDto, "productName"),
    (ShippersDto, "companyName"),
    (SuppliersDto, "companyName"),
]

# Integer key and foreign-key properties bounded to 1..2147483647.
INT32_KEYS = [
    (CategoriesDto, "categoryId"),
    (EmployeesDto, "employeeId"),
    (EmployeesDto, "reportsTo"),
    (OrderDetailsDto, "orderId"),
    (OrderDetailsDto, "productId"),
    (OrdersDto, "employeeId"),
    (OrdersDto, "orderId"),
    (OrdersDto, "shipVia"),
    (ProductsDto, "categoryId"),
    (ProductsDto, "productId"),
    (ProductsDto, "supplierId"),
    (ShippersDto, "shipperId"),
    (SuppliersDto, "supplierId"),
]


def _ids(cases: list[tuple]) -> list[str]:
    return [f"{case[0].__name__}.{case[1]}" for case in cases]


@pytest.mark.parametrize("dto_type", MINIMAL_PAYLOADS, ids=lambda dto: dto.__name__)
def test_dto_minimal_payload_is_accepted(dto_type: type[BaseModel]) -> None:
    dto_type.model_validate(MINIMAL_PAYLOADS[dto_type])


@pytest.mark.parametrize(("dto_type", "field", "max_length"), MAX_LENGTHS, ids=_ids(MAX_LENGTHS))
def test_dto_string_at_max_length_is_accepted(
    dto_type: type[BaseModel], field: str, max_length: int
) -> None:
    payload = {**MINIMAL_PAYLOADS[dto_type], field: "x" * max_length}

    assert getattr(dto_type.model_validate(payload), field) == "x" * max_length


@pytest.mark.parametrize(("dto_type", "field", "max_length"), MAX_LENGTHS, ids=_ids(MAX_LENGTHS))
def test_dto_string_over_max_length_is_rejected(
    dto_type: type[BaseModel], field: str, max_length: int
) -> None:
    payload = {**MINIMAL_PAYLOADS[dto_type], field: "x" * (max_length + 1)}

    with pytest.raises(ValidationError) as error:
        dto_type.model_validate(payload)
    assert error.value.errors()[0]["loc"][0] == field


@pytest.mark.parametrize(("dto_type", "field"), REQUIRED_TEXT, ids=_ids(REQUIRED_TEXT))
@pytest.mark.parametrize("value", [None, ""], ids=["null", "empty"])
def test_dto_required_text_null_or_empty_is_rejected(
    dto_type: type[BaseModel], field: str, value: str | None
) -> None:
    payload = {**MINIMAL_PAYLOADS[dto_type], field: value}

    with pytest.raises(ValidationError):
        dto_type.model_validate(payload)


@pytest.mark.parametrize(("dto_type", "field"), REQUIRED_TEXT, ids=_ids(REQUIRED_TEXT))
def test_dto_required_text_missing_is_rejected(dto_type: type[BaseModel], field: str) -> None:
    payload = {key: value for key, value in MINIMAL_PAYLOADS[dto_type].items() if key != field}

    with pytest.raises(ValidationError):
        dto_type.model_validate(payload)


@pytest.mark.parametrize(("dto_type", "field"), INT32_KEYS, ids=_ids(INT32_KEYS))
@pytest.mark.parametrize("value", [0, 2147483648])
def test_dto_int32_key_out_of_range_is_rejected(
    dto_type: type[BaseModel], field: str, value: int
) -> None:
    payload = {**MINIMAL_PAYLOADS[dto_type], field: value}

    with pytest.raises(ValidationError):
        dto_type.model_validate(payload)


@pytest.mark.parametrize("customer_id", ["ALFK", "ALFKIX"])
def test_customer_id_not_five_characters_is_rejected(customer_id: str) -> None:
    with pytest.raises(ValidationError):
        CustomersDto(customerId=customer_id, companyName="Alfreds Futterkiste")


def test_customer_id_null_is_rejected() -> None:
    with pytest.raises(ValidationError):
        CustomersDto(customerId=None, companyName="Alfreds Futterkiste")


def test_order_customer_id_may_be_null_but_not_short() -> None:
    assert OrdersDto(customerId=None).customerId is None
    with pytest.raises(ValidationError):
        OrdersDto(customerId="ALF")


def test_order_freight_accepts_negative_value() -> None:
    assert OrdersDto(freight=-1.25).freight == -1.25


@pytest.mark.parametrize("field", ["orderDate", "requiredDate", "shippedDate"])
def test_order_date_before_1753_is_rejected(field: str) -> None:
    with pytest.raises(ValidationError):
        OrdersDto.model_validate({field: "1752-12-31T00:00:00"})


def test_employee_birth_date_in_future_is_rejected() -> None:
    with pytest.raises(ValidationError, match="earlier than the current date"):
        EmployeesDto(firstName="Nancy", lastName="Davolio", birthDate="9999-01-01T00:00:00")


def test_employee_hire_date_in_future_is_accepted() -> None:
    dto = EmployeesDto(firstName="Nancy", lastName="Davolio", hireDate="9999-01-01T00:00:00")

    assert dto.hireDate.year == 9999


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("discount", -0.01),
        ("discount", 1.01),
        ("quantity", 0),
        ("quantity", 32768),
        ("unitPrice", -0.01),
    ],
)
def test_order_detail_out_of_range_value_is_rejected(field: str, value: float) -> None:
    payload = {**MINIMAL_PAYLOADS[OrderDetailsDto], field: value}

    with pytest.raises(ValidationError):
        OrderDetailsDto.model_validate(payload)


def test_order_detail_discount_bounds_are_inclusive() -> None:
    payload = MINIMAL_PAYLOADS[OrderDetailsDto]

    assert OrderDetailsDto.model_validate({**payload, "discount": 1}).discount == 1
    assert OrderDetailsDto.model_validate({**payload, "discount": 0}).discount == 0


@pytest.mark.parametrize("field", ["reorderLevel", "unitsInStock", "unitsOnOrder"])
def test_product_stock_level_omitted_defaults_to_zero(field: str) -> None:
    assert getattr(ProductsDto(productName="Chai"), field) == 0


@pytest.mark.parametrize("field", ["reorderLevel", "unitsInStock", "unitsOnOrder"])
def test_product_stock_level_explicit_null_is_kept(field: str) -> None:
    dto = ProductsDto.model_validate({"productName": "Chai", field: None})

    assert getattr(dto, field) is None


@pytest.mark.parametrize("field", ["reorderLevel", "unitsInStock", "unitsOnOrder"])
@pytest.mark.parametrize("value", [-1, 32768])
def test_product_stock_level_out_of_range_is_rejected(field: str, value: int) -> None:
    with pytest.raises(ValidationError):
        ProductsDto.model_validate({"productName": "Chai", field: value})


def test_product_unit_price_negative_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ProductsDto(productName="Chai", unitPrice=-1)

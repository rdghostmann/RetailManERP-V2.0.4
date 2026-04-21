from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    phone: str
    role: str


@dataclass
class Product:
    id: int
    name: str
    brand: str
    description: str


@dataclass
class Stock:
    id: int
    product_id: int
    imei: str
    colour: str
    quantity: int
    batch_no: str
    added_by: str


@dataclass
class Log:
    id: int
    user_id: int
    action: str
    table_name: str
    record_id: int
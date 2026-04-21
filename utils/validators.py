from app.config import InventoryConfig, Messages


class Validators:

    @staticmethod
    def validate_required(value, message="Field is required"):
        if value is None or str(value).strip() == "":
            raise ValueError(message)

    @staticmethod
    def validate_imei(imei: str):
        Validators.validate_required(imei, Messages.IMEI_REQUIRED)

        if not imei.isdigit() or len(imei) != InventoryConfig.IMEI_LENGTH:
            raise ValueError(Messages.IMEI_INVALID)

    @staticmethod
    def validate_quantity(quantity):
        if int(quantity) <= 0:
            raise ValueError("Quantity must be greater than 0")

    @staticmethod
    def validate_phone(phone: str):
        Validators.validate_required(phone, "Phone number is required")

        if not phone.isdigit() or len(phone) < 10:
            raise ValueError("Invalid phone number")

    @staticmethod
    def validate_product_name(name: str):
        Validators.validate_required(name, Messages.PRODUCT_REQUIRED)
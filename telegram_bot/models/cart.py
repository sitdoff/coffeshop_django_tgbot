from decimal import Decimal

from models.models import ProductModel
from pydantic import BaseModel


class Cart(BaseModel):
    items: dict[str | int, ProductModel] = {}

    @property
    def total_cost(self):
        return sum(Decimal(item.cost) for item in self.items.values())

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data["items"] = {key: item.model_dump(by_alias=True) for key, item in self.items.items()}
        data["total_cost"] = self.total_cost
        return data

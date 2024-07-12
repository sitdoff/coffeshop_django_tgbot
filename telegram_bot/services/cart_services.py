def get_product_dict_from_redis(
    product_str: str, template: str = "id:name:price:quantity:cost", delimeter: str = ":"
) -> dict:
    keys = template.split(delimeter)
    values = product_str.split(delimeter)
    return dict(zip(keys, values))


def get_product_model_from_redis(product_dict: dict) -> ProductModel:
    return ProductModel(**product_dict, is_data_from_redis=True)

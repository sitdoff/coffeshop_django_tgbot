def get_product_str_for_redis(
    product_dict: dict, template: str = "id:name:price:quantity:cost", delimeter: str = ":"
) -> str:
    keys = template.split(delimeter)
    values = [str(product_dict.get(key, "")) for key in keys]
    return delimeter.join(values)


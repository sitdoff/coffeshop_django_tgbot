from django.shortcuts import get_object_or_404, render
from goods.models import ProductModel
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .cart import Cart
from .serializers import CartSerializer

# Create your views here.


class CartView(APIView):

    def get(self, request: Request, format=None) -> Response:
        """
        Method: GET. Retrieving the contents of the cart.
        """
        cart = Cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    # def post(self, request: Request, *args, **kwargs) -> Response:
    #     ...

    def put(self, request: Request, *args, override_quantity: bool = False, **kwargs) -> Response:
        """
        Method PUT. Add the item to your cart.

        Waiting JSON:
        {
            "id": int,
            "quantity": int
        }

        "id" - required
        "quantity" - must be greater than 0. If not specified, the product is added in quantity 1.

        If override_quantity is True, the new quantity value replaces the old one.
        """
        cart = Cart(request)
        product = get_object_or_404(ProductModel, pk=request.data["id"])
        if "quantity" not in request.data:
            cart.add(product)
        else:
            quantity = int(request.data["quantity"])
            cart.add(product, quantity=quantity, override_quantity=override_quantity)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def patch(self, request: Request, *args, **kwargs) -> Response:
        """
        Method PATCH. Changes the quantity of an item.
        """
        return self.put(request, *args, override_quantity=True, **kwargs)

    def delete(self, request: Request, *args, **kwargs) -> Response:
        """
        Method DELETE. Removes an item from the cart.
        """
        cart = Cart(request)
        cart.clear()
        return self.get(request, *args, **kwargs)

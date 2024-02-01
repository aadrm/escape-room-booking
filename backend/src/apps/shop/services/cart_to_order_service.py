from ..models import Cart, Order, OrderItem
from . import CartItemPriceCalculatorService

class CartToOrderService:

    @staticmethod
    def cart_to_order(cart: Cart):
        # clean cart
        items = cart.get_cartitem_set()
        order = Order.objects.create(
            cart=cart

        )
        for item in items:
            CartToOrderService.add_cart_item_to_order(item, order)

    @staticmethod
    def add_cart_item_to_order(item: OrderItem, order: Order):
        order.add_item(
            reference=CartToOrderService.cart_item_details_to_order_item_reference(item),
            base_price=CartItemPriceCalculatorService.get_item_base_price(item),
            gross_price=CartItemPriceCalculatorService.calculate_price(item),
            vat_factor=item.product.vat_factor,
        )

    @staticmethod
    def cart_item_details_to_order_item_reference(item: OrderItem) -> str:
        return item.product.name

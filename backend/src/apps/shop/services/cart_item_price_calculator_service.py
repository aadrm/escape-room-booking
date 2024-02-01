from decimal import Decimal

from apps.shop.models import CartItem, CartItemCoupon

class CartItemPriceCalculatorService:
    """ This service provides a way to calculate the price of an
        item in the cart taking into consideration the coupons applied
        and how they interact with other items in the cart.
    """
    @staticmethod
    def calculate_price(cart_item) -> Decimal:
        cart = cart_item.cart
        items = cart.get_cartitem_set()
        coupons = cart.coupons.all().order_by('coupon__is_percent')
        # create an array of [item, base_price] to have persistance during the
        # calculations of each cart item price
        item_price_list = CartItemPriceCalculatorService.produce_cart_item_price_list(items)

        CartItemPriceCalculatorService.apply_coupons(cart, coupons, item_price_list)
        return CartItemPriceCalculatorService.retrieve_gross_price_from_list(cart_item, item_price_list)

    @staticmethod
    def produce_cart_item_price_list(items):
        item_price_list = []
        for item in items:
            item_base_price = CartItemPriceCalculatorService.get_item_base_price(item)
            item_price_list.append([item, item_base_price])
        return item_price_list

    @staticmethod
    def get_item_base_price(item: CartItem):
        base_price = item.product.base_price
        if hasattr(item, 'cartitemcoupon'):
            item = CartItemCoupon.objects.get(pk=item.cartitemcoupon.pk)
            base_price += item.cartitemcoupon.product.product_group.productgroupcoupon.shipping_cost
        return base_price

    @staticmethod
    def apply_coupons(cart, coupons, item_price_list):
        for cart_coupon in coupons:
            coupon = cart_coupon.coupon
            if cart.get_total_base_price() >= coupon.minimum_spend:
                if coupon.is_percent:
                    CartItemPriceCalculatorService.apply_percent_coupon(coupon, item_price_list)
                else:
                    CartItemPriceCalculatorService.apply_absolute_coupon(coupon, item_price_list)

    @staticmethod
    def apply_percent_coupon(coupon, item_price_list):
        for item_price_pair in item_price_list:
            if coupon.is_applicable_to_item(item_price_pair[0]):
                item_price_pair[1] = coupon.calculate_discounted_price(item_price_pair[1])
                if not coupon.apply_to_entire_cart:
                    break

    @staticmethod
    def apply_absolute_coupon(coupon, item_price_list):
        coupon_value_used = 0
        for item_price_pair in item_price_list:
            if coupon.is_applicable_to_item(item_price_pair[0]):
                price_before_calc = item_price_pair[1]
                item_price_pair[1] = coupon.calculate_discounted_price(item_price_pair[1] + coupon_value_used)
                coupon_value_used = price_before_calc - item_price_pair[1]
                if not coupon.apply_to_entire_cart:
                    break

    @staticmethod
    def retrieve_gross_price_from_list(item, item_price_list):
        for item_price_pair in item_price_list:
            if item_price_pair[0].pk == item.pk:
                return item_price_pair[1]


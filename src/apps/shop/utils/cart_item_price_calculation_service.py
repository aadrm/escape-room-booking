from decimal import Decimal

class CartItemPriceCalculatorService:
    """ This service provides a way to calculate the price of an
        item in the cart taking into consideration the coupons applied
        and how they interact with other items in the cart.
    """
    @classmethod
    def calculate_price(cls, cart_item, coupons, items) -> Decimal:
        item_price_list = [[item, item.base_price] for item in items]
        cls.apply_coupons(coupons, item_price_list)
        return cls.get_item_price(cart_item, item_price_list)

    @classmethod
    def apply_coupons(cls, coupons, item_price_list):
        for cart_coupon in coupons:
            coupon = cart_coupon.coupon
            cart_total = sum(item[1] for item in item_price_list)
            if cart_total >= coupon.minimum_spend:
                if coupon.is_percent:
                    cls.apply_percent_coupon(coupon, item_price_list)
                else:
                    cls.apply_absolute_coupon(coupon, item_price_list)

    @classmethod
    def apply_percent_coupon(cls, coupon, item_price_list):
        for item_price_pair in item_price_list:
            if coupon.is_applicable_to_item(item_price_pair[0]):
                item_price_pair[1] = coupon.calculate_discounted_price(item_price_pair[1])
                if not coupon.apply_to_entire_cart:
                    break

    @classmethod
    def apply_absolute_coupon(cls, coupon, item_price_list):
        coupon_value_used = 0
        for item_price_pair in item_price_list:
            if coupon.is_applicable_to_item(item_price_pair[0]):
                price_before_calc = item_price_pair[1]
                item_price_pair[1] = coupon.calculate_discounted_price(item_price_pair[1] + coupon_value_used)
                coupon_value_used = price_before_calc - item_price_pair[1]
                if not coupon.apply_to_entire_cart:
                    break

    @classmethod
    def get_item_price(cls, item, item_price_list):
        for item_price_pair in item_price_list:
            if item_price_pair[0].pk == item.pk:
                return item_price_pair[1]


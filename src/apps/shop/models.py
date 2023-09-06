from datetime import timedelta
from django.db import models
from django.utils.translation import gettext as _
from decimal import Decimal

from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string, get_template
from breakout.utils import textify, get_booking_settings
from django.conf import settings

from ..models import PaymentMethod
from apps.booking.coupon.models import Coupon

from weasyprint import HTML, CSS

class Cart(models.Model):
    """
    Shopping Cart

    A cart is created for every session. 
    Producs and coupons are added to a cart by using the models CartItem and CartCoupon.
    """

    status = models.SmallIntegerField("status", default=0)
    items_before_checkout = models.SmallIntegerField("items before purchase", blank=True, null=True)
    invoice = models.OneToOneField("booking.Invoice", verbose_name="Invoice", on_delete=models.PROTECT, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    subtotal = models.DecimalField('Subtotal', max_digits=6, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=6, decimal_places=2, default=0)

    @property
    def is_require_shipping_address(self):
        for item in self.cart_items.all():
            if item.product.family.shipping_cost:
                return True
        return False

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse("Cart_detail", kwargs={"pk": self.pk})

    def apply_coupons(self):
        self.reset_cart_items()
        self.clear_non_valid_items()
        cart_coupons = self.cart_coupons.all()
        cart_items = self.cart_items.all()
        for coupon in cart_coupons:
            try:
                cp = coupon.coupon
                applicable_products = cp.products_applicable_queryset()
                applied = False
                #  used for cases where a fixed amount discount that applies to the entire basquet
                #  has more value than the current item of the basquet, so the rest of the coupon
                #  will be applied to the next item
                cumulative_discount = 0
                for item in cart_items:
                    print(applicable_products)
                    applicable_to_product = cp.is_applicable(item.product)
                    applicable_to_slot = True
                    if item.slot:
                        if not item.slot.start.weekday() in cp.dow_as_integerlist:
                            applicable_to_slot = False
                    if applicable_to_product and applicable_to_slot:
                        if coupon.no_coupon_conflict(item):
                            cumulative_discount = coupon.add_to_cart_item(item, cumulative_discount)
                            applied = True
                            if not (cp.is_apply_to_basket) or not (cp.is_percent) and cumulative_discount >= cp.amount:
                                break
            except Exception as e:
                print(e)

    def reset_cart_items(self):
        self.reset_cart_items_price()
        self.reset_cart_items_coupons()
        self.reset_cart_coupons()

    def reset_cart_items_price(self):
        self.clear_non_valid_items()
        for item in self.cart_items.all():
            item.set_price()
            item.save()

    def reset_cart_items_coupons(self):
        self.clear_non_valid_items()
        for item in self.cart_items.all():
            item.cart_coupons.clear()
            item.save()
    
    def reset_cart_coupons(self):
        for coupon in self.cart_coupons.all():
            try:
                coupon.discount = 0
                coupon.save()
            except Exception:
                coupon.delete()

    def clear_non_valid_items(self):
        items = self.cart_items.all()
        for item in items:
            if not item.is_in_cart:
                item.delete()

    def get_appointment_items(self):
        self.clear_non_valid_items()
        valid_items = self.cart_items.all()
        appointment_items = []
        for item in valid_items:
            if item.slot:
                appointment_items.append(item)
        return appointment_items

    def get_coupon_items(self):
        self.clear_non_valid_items()
        valid_items = self.cart_items.all()
        coupon_items = []
        for item in valid_items:
            if item.product.family.is_coupon:
                coupon_items.append(item)
        return coupon_items

    def print_items_prices(self):
        print('---items---')
        for item in self.cart_items.all():
            print(f'{item}: price {item.price} base {item.price}')

    def get_valid_payment_methods(self):
        methods_prev = PaymentMethod.objects.filter(method='coupon')
        if self.total > 0:
            items = self.cart_items.all()
            methods_prev = PaymentMethod.objects.all()
            methods_curr = PaymentMethod.objects.all()
            for item in items:
                methods_curr = item.product.family.payment_methods.all()
                methods_prev = methods_curr.intersection(methods_prev)
        return methods_prev

    def number_of_valid_items(self):
        """return the number of valid items, useful in the templates"""
        itemsList = list(self.cart_items.all())
        return len(itemsList)

    def update_valid_items(self):
        """this method checks the valid items currently on the cart
        meant to save this 'status' during checkout and later compare this number
        when trying to execute payment and accept the transaction if both numbers match
        """
        self.items_before_checkout = self.number_of_valid_items()
        self.save()

    def set_subtotal(self):
        """The sum of the price of the valid items in the cart"""
        total = 0
        for item in self.cart_items.all():
            total += item.base_price
        self.subtotal = total
        self.save()
    
    def set_total(self):
        """The sum of the price of the valid items in the cart
        after the discount of the coupons in the cart is applied"""
        total = 0
        for item in self.cart_items.all():
            total += item.price
        self.total = total
        self.save()

    def discount(self):
        """
        Subtraction between total and total_after_coupons
        """
        return self.total - self.subtotal

    def extend_items_expiration(self):
        """calls the extend expiration method for each of the cart items"""
        self.clear_non_valid_items()
        for item in self.cart_items.all():
            item.extend_expiration()

    def use_coupons(self):
        """
        Calls the function that increases the use counter for each coupon in the cart
        """
        for coupon in self.cart_coupons.all():
            coupon.coupon.add_used_time()
    
    def approve_items(self):
        """
        sets the status of all the items of the cart to 1 which means that
        each item has ben purchased
        """
        for item in self.cart_items.all():
            item.set_approved()
            item.save()

    def create_cart_coupons(self, paid=True):
        coupon_items = self.get_coupon_items()
        for item in coupon_items:
            if item.coupon:
                coupon = item.coupon
            else:
                coupon = Coupon()

            value = item.product.value
            coupon_ref = ''
            coupon_ref += self.invoice.order_number
            coupon_ref = ' | '
            coupon_ref += item.product.__str__()
            coupon.use_limit = 1 if paid else -1
            coupon.name = coupon_ref
            coupon.is_apply_to_basket = True
            coupon.amount = value
            coupon.is_overrule_individual_use = False
            coupon.is_individual_use = False
            coupon.save()

            item.coupon = coupon
            item.save()

    def paypal_preapprove(self):
        if self.status < 1:
            self.status = 2
            self.invoice.commit_order()
            self.create_cart_coupons(paid=False)
            self.save()

    def approve_cart(self):
        """
        sets the status of the cart to 1 which means that the order should be confirmed
        """
        self.approve_items()
        self.use_coupons()
        self.status = 1
        self.save()

    def process_purchase(self):
        try:
            self.approve_cart()
            self.invoice.commit_order()
            self.create_cart_coupons()
            return True
        except Exception as e:
            print(e)
            return False

    def send_cart_emails(self):
        cart = self
        invoice = cart.invoice
        context = {
            'invoice': invoice,
            'cart': cart,
            'domain': 'breakout-escaperoom.de',
            'appointments': cart.get_appointment_items(),
            'coupons': cart.get_coupon_items(),
            'payment': invoice.payment,
        }

        html_message = render_to_string(
            'email/order_confirmation.html', context)
        message = textify(html_message)
        to_email = invoice.email
        mail_subject = _('Breakout Escape Room | Order: ') + \
            invoice.order_number
        email = EmailMultiAlternatives(
            subject=mail_subject,
            body=message,
            from_email='info@breakout-escaperoom.de',
            to=[to_email, ],
        )

        email.attach_alternative(html_message, mimetype='text/html')
        self.attach_cart_coupons_to_email(email)
        email.send(fail_silently=True)

        mail_subject = _('Breakout Escape Room | Order: ') + \
            invoice.order_number
        html_message = render_to_string(
            'email/order_confirmation_alert.html', context)
        message = textify(html_message)

        email = EmailMultiAlternatives(
            subject=mail_subject,
            body=message,
            from_email='info@breakout-escaperoom.de',
            to=['info@breakout-escaperoom.de', ],
        )
        email.attach_alternative(html_message, mimetype='text/html')
        email.send(fail_silently=True)

    def attach_cart_coupons_to_email(self, email):
        """given an EmailMessage this function will create the pdf files of the coupons that
        were purchased in that order and attache them to the email message"""
        for coupon in self.get_coupon_items():
            context = {
                'coupon': coupon.coupon,
            }
            html_string = render_to_string(
                'booking/pdf-coupon_code.html', context)
            html = HTML(string=html_string, base_url=settings.BASE_URL)
            # html = HTML(string=html_string, base_url=request.build_absolute_uri())
            csspath = settings.STATIC_ROOT + 'css/pdf/coupon_code.css'
            pdf = html.write_pdf(stylesheets=[CSS(csspath)])
            email.attach(_('gift_voucher_') + coupon.coupon.code + '.pdf', pdf)

    def remove_item(self, id):
        items = self.cart_items.all()
        item = items.get(pk=id)
        item.delete()

    def delete_order(self):
        """
        deletes the order and any related data
        """
        for item in self.cart_items.all():
            item.delete()
        for item in self.cart_coupons.all():
            item.coupon.used_times -= 1
            item.coupon.save()
            item.delete()
        invoice = self.invoice
        self.delete()
        invoice.delete()

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))


class CartItem(models.Model):
    """
    Model that acts as a bridge between products and the cart
    """

    @classmethod
    def create(cls, product, cart, slot=None):
        print('creating item')
        print(product, product.price, cart)
        return cls(product=product, base_price=product.price, cart=cart, slot=slot)

    slot = models.ForeignKey("booking.Slot", related_name="cart_items", verbose_name=_(
        "slot"), on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ForeignKey("booking.Coupon", related_name="booking",
                               on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey("booking.Product", on_delete=models.PROTECT)
    status = models.SmallIntegerField(_("status"), default=0)
    cart = models.ForeignKey("booking.Cart", verbose_name=_("Cart"), related_name=_(
        "cart_items"), on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)
    base_price = models.DecimalField(
        _("Price"), max_digits=8, decimal_places=2)
    price = models.DecimalField(
        _("Price"), max_digits=8, decimal_places=2)
    cart_coupons = models.ManyToManyField("booking.CartCoupon", verbose_name=_(
        "coupons"), related_name='cart_items', blank=True)
    marked_shipped = models.DateTimeField(
        _("Shipped"), auto_now=False, auto_now_add=False, null=True, blank=True)


    @property
    def is_appointment(self):
        True if self.slot else False

    @property
    def is_coupon(self):
        True if self.product.family.is_coupon else False

    @property
    def base_price_at_booking(self):
        discount = 0
        if self.slot:
            discount = self.slot.incentive_discount()
        return self.product.price - Decimal(discount)

    @property
    def incentive_discount(self):
        return


    @property
    def is_slot_booked(self):
        """
        Returns True if there is a slot associated with this item and either 
        the booking was completed or is being booked and the expiry time has not been reached
        """
        if self.slot:
            this_moment = timezone.now()
            if self.status > 0:
                return True
            elif self.status == 0 and this_moment < self.item_expiry():
                return True
            else:
                return False
        else:
            return False

    @property
    def is_in_cart(self):
        """this means that the item is part of it's related cart, the conditions are if 
        this item is not expired
        """
        if self.slot and self.status == 1:
            return True
        elif self.slot and self.status == 0 and self.item_expiry_seconds() < 1:
            return False
        elif self.status < 0:
            return False
        else:
            return True

    def set_price(self):
        self.price = Decimal(self.base_price_at_booking)

    def save(self, request=None, *args, **kwargs):
        """
        Custom save method, sets the price of the CartItem to be the same as the product's
        This price is the one to be modified by any discounts applied.
        """

        if self.pk is None:
            self.set_price()

        super(CartItem, self).save(*args, **kwargs)


    def item_expiry(self):
        """
        returns the datetime of expiration for this item, only affects the item if it has 
        a related slot and status is 0 
        """
        if self.slot:
            return self.created + timedelta(minutes=get_booking_settings().slot_reservation_hold_minutes)
        else:
            False

    def item_expiry_seconds(self):
        if self.slot and self.status == 0:
            this_moment = timezone.now()
            expiry = self.item_expiry()
            # this condition allows some extra time for orders carried out via paypal IPN
            if self.cart.status > 0:
                return ((expiry + timedelta(minutes=40)) - this_moment).total_seconds()
            else:
                return (expiry - this_moment).total_seconds()
        else:
            return 0

    def extend_expiration(self):
        self.created = timezone.now() 
        self.save()

    def set_approved(self):
        self.status = 1
        self.save()
    
    def has_individual_use_coupon(self):
        if self.cart_coupons.filter(coupon__is_individual_use=True):
            return True
        else:
            return False

    def has_neutral_coupon(self):
        if self.cart_coupons.filter(coupon__is_overrule_individual_use=False):
            return True
        else:
            return False

    def get_admin_url(self):
        return reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name), args=(self.id,))


class CartCoupon(models.Model):

    coupon = models.ForeignKey("booking.Coupon", verbose_name=_("Cart Coupon"), null=True, on_delete=models.SET_NULL, )
    cart = models.ForeignKey("booking.Cart", verbose_name=_("Cart"), related_name=_("cart_coupons"), on_delete=models.CASCADE, null=True, blank=True)
    discount = models.DecimalField(_("Discount"), max_digits=8, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("CartCoupon")
        verbose_name_plural = _("CartCoupons")
        ordering = [
            '-coupon__is_upgrade',
            'coupon__is_percent',
            'coupon__is_apply_to_basket',
        ]

    def __str__(self):
        return self.coupon.__str__()

    def get_absolute_url(self):
        return reverse("CartCoupon_detail", kwargs={"pk": self.pk})

    def save(self, request=None, *args, **kwargs):

        """Custom save method checks if the coupon is not already in the cart"""
        if request:
            if self.cart.cart_coupons.filter(coupon__pk=self.coupon.pk).exists():
                messages.add_message(
                    request,
                    messages.WARNING,
                    _('The coupon with the code "%(code)s" is already being applied to your purchase.') % 
                    {'code': self.coupon.code}
                )
            elif self.coupon and self.coupon.is_expired:
                messages.add_message(
                    request,
                    messages.WARNING,
                    _('The coupon "%(code)s" is expired') %
                    {'code': self.coupon.code}

                )
            elif self.coupon and self.coupon.is_overused:
                messages.add_message(
                    request,
                    messages.WARNING,
                    _('The "%(code)s" has exceeded its usage limit') %
                    {'code': self.coupon.code}
                )
            else:
                messages.add_message(
                    request,
                    messages.INFO,
                    _('Coupon "%(code)s" successfully added to your cart') %
                    {'code': self.coupon.code}
                )
                super(CartCoupon, self).save(*args, **kwargs)
        else:
            super(CartCoupon, self).save(*args, **kwargs)

    def no_coupon_conflict(self, cart_item):
        if self.coupon.is_overrule_individual_use:
            return True
        elif self.coupon.is_individual_use:
            if not(cart_item.has_neutral_coupon()):
                return True 
            else:
                return False
        else:
            if not(cart_item.has_individual_use_coupon()):
                return True 
            else:
                return False 

    def add_to_cart_item(self, item, cumulative_discount):
        cumulative_discount = self.coupon.apply_to_cart_item(item, cumulative_discount, self)
        self.discount = cumulative_discount
        self.save()
        return cumulative_discount

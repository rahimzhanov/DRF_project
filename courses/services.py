# courses/services.py
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name, description):
    """
    Создает продукт в Stripe
    """
    try:
        product = stripe.Product.create(
            name=name,
            description=description,
        )
        return product
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return None


def create_stripe_price(amount, product_id):
    """
    Создает цену для продукта в Stripe
    amount - в рублях (будет преобразовано в копейки)
    """
    try:
        # Конвертируем рубли в копейки (умножаем на 100)
        amount_in_cents = int(amount * 100)

        price = stripe.Price.create(
            unit_amount=amount_in_cents,
            currency='rub',
            product=product_id,
        )
        return price
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return None


def create_stripe_checkout_session(price_id, success_url, cancel_url):
    """
    Создает сессию для оплаты
    Возвращает URL для оплаты
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return None


def get_stripe_session_status(session_id):
    """
    Получает статус сессии оплаты
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return None
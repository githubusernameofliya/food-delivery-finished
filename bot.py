from datetime import datetime

from database import register_user, get_categories, get_category_products, get_product, add_to_cart, get_user_id, get_cart_product_quantity, update_product_quantity, get_users_cart_amount, get_users_products_in_cart, add_to_order_history, clean_users_cart, get_users_order_history
from keyboards import generate_categories_menu, generate_category_products_menu, generate_product_menu, generate_main_menu, generate_pay_button
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery, LabeledPrice, ShippingQuery, ShippingOption, PreCheckoutQuery
from aiogram.dispatcher.filters import Text
from aiogram.types.message import ContentTypes

PAYMENT_PROVIDER_TOKEN = "284685063:TEST:OTBiZDcxZWRlYzg4"
TOKEN = "6961881359:AAH5EL9FZIH6MKNnsQAzrynyFJnhAYVQc0s"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)



@dp.message_handler(commands="start")
@dp.message_handler(Text(equals="🚚📦💵 Order"))
async def say_hello(message: Message):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name

    try:
        register_user(telegram_id=str(telegram_id), full_name=full_name)
        caption = f"Hi {full_name} 👋\nHow can I help you ?"
    except:
        caption = f"Hi {full_name} 👋\nWelcome back !"

    categories = get_categories()

    with open(file="images/main_photo.jpeg", mode="rb") as photo:
        await message.reply_photo(
            photo=photo,
            caption=caption,
            reply_markup=generate_categories_menu(categories=categories)
        )

    await bot.send_message(chat_id=message.from_user.id,
                           text="Select a category",
                           reply_markup=generate_main_menu())


@dp.message_handler(Text(equals="📋 Main menu"))
async def show_main_menu(message: Message):
    categories = get_categories()

    with open(file="images/main_photo.jpeg", mode="rb") as photo:
        await message.reply_photo(
            photo=photo,
            caption="📋 Main menu",
            reply_markup=generate_categories_menu(categories=categories)
        )


@dp.message_handler(commands="cart")
@dp.message_handler(Text(equals="🛒 My cart"))
async def show_cart(message: Message):
    user_id = get_user_id(message.from_user.id)
    products = get_users_products_in_cart(user_id)

    prices = []
    text = ""

    for cart_product in products:  # ((1, 1, 1, 3, 3.60), (2, 1, 2, 3, 4.20))
        product = get_product(product_id=cart_product[2])
        product_name = product[2]
        prices.append(
            LabeledPrice(label=product_name, amount=int(
                float(cart_product[-1]) * 100))
        )
        text += f"{product_name}, x{cart_product[-2]}\n"
        text += f"{product[-2]} x {cart_product[-2]} = {cart_product[-1]} USD\n\n"

    if len(products) == 0:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="🤔 Your cart is empty",
        )
    else:
        await bot.send_invoice(
            chat_id=message.from_user.id,
            provider_token=PAYMENT_PROVIDER_TOKEN,
            title="🛒 Your cart",
            description=text,
            prices=prices,
            currency="usd",
            photo_url="https://media01.stockfood.com/largepreviews/MzQ3MjA3NDQw/11200240-Grocery-Cart-Full-of-Food.jpg",
            need_name=True,
            need_email=True,
            need_phone_number=True,
            need_shipping_address=True,
            payload=f"user_id:{user_id[0]}",
            start_parameter="liyas-payment-bot",
            is_flexible=True,
        )


@dp.message_handler(Text(equals="📄 My orders"))
async def show_orders_history(message: Message):

    # Get user's orders from orders history table
    user_id = get_user_id(telegram_id=message.from_user.id)
    order_histroy_products = get_users_order_history(user_id=user_id)

    # Generate a template based on user's orders history
    text = "🛒 Your orders history\n\n"

    for order_history_product in order_histroy_products:
        product = get_product(product_id=order_history_product[-1])

        text += f"{order_history_product[3]}\n"
        text += f"{product[2]} - {order_history_product[2]}\n\n"

    # Send the generated message
    if len(order_histroy_products) == 0:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="You haven't ordered anything yet",
        )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=text,
        )


@dp.shipping_query_handler()
async def return_shipping_options(shipping_query: ShippingQuery):
    shipping_options = [
        ShippingOption(id="fast", title="World wide teleport", prices=[
                       LabeledPrice(label="As soon as possible", amount=10000)]),
        ShippingOption(id="normal", title="Within 30 days", prices=[
                       LabeledPrice(label="Normal delivery", amount=2000)]),
    ]

    await bot.answer_shipping_query(
        shipping_query_id=shipping_query.id,
        shipping_options=shipping_options,
        ok=True,
        error_message="Oops, looks like we out of theese products"
    )


@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query: PreCheckoutQuery):
    splitted_payload = pre_checkout_query.invoice_payload.split(
        ":")  # "user_id:4" => ["user_id", "1"]
    user_id = int(splitted_payload[-1])
    now = datetime.now().strftime(
        "%Y-%m-%d %H:%m:%s")[:19]  # 2024-05-10 19:45:10

    # Get latest order of that user
    products = get_users_products_in_cart(user_id=user_id)

    # Create order history based on the latest order of the user
    for product in products:
        total_price = product[-1]
        add_to_order_history(user_id=user_id, total_price=total_price,
                             created_datetime=now, product_id=product[2])

    # Clean the user's cart
    clean_users_cart(user_id=user_id)

    await bot.answer_pre_checkout_query(
        pre_checkout_query_id=pre_checkout_query.id,
        ok=True,
    )


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def got_payment(message: Message):
    total_amount = message.successful_payment.total_amount / 100
    currency = message.successful_payment.currency.capitalize()

    text = f"""Hoooooray! Thanks for the payment!
We will proceed with your order for `{total_amount} {currency}` as fast as possible!
Stay in touch"""

    await bot.send_message(
        chat_id=message.chat.id,
        text=text
    )


@dp.callback_query_handler()
async def handle_callback(call: CallbackQuery):
    splitted_call = call.data.split(":")  # "category:1" => ["category", "1"]

    if splitted_call[0] == "category":
        category_id = splitted_call[1]

        products = get_category_products(category_id=category_id)

        await bot.edit_message_caption(chat_id=call.message.chat.id,
                                       message_id=call.message.message_id,
                                       caption="All products for this category",
                                       reply_markup=generate_category_products_menu(
                                           products=products
                                       ))

    elif splitted_call[0] == "product":
        product_id = splitted_call[-1]

        product = get_product(product_id=product_id)  # (1, 1, "Burger", ...)

        text = f"<b>Product name: {product[2]}\n\n{product[-1]}\n\nPrice: ${product[-2]}</b>"

        await bot.send_message(chat_id=call.from_user.id,
                               text=text,
                               reply_markup=generate_product_menu(
                                   category_id=product[1],
                                   product_id=product_id),
                               parse_mode="HTML")
        await call.message.delete()

    elif splitted_call[0] == "back":
        if splitted_call[1] == "categories":
            categories = get_categories()
            await bot.edit_message_caption(chat_id=call.message.chat.id,
                                           message_id=call.message.message_id,
                                           caption="All categories",
                                           reply_markup=generate_categories_menu(categories))

        elif splitted_call[1] == "category":

            category_id = int(splitted_call[-1])
            products = get_category_products(category_id=category_id)

            with open(file="images/main_photo.jpeg", mode="rb") as photo:
                await bot.send_photo(chat_id=call.message.chat.id,
                                     photo=photo,
                                     caption="All products for this category",
                                     reply_markup=generate_category_products_menu(products=products))

            await call.message.delete()

    elif splitted_call[0] == "quantity":
        action = splitted_call[1]

        if action == "increment":
            new_quantity = int(splitted_call[-1]) + 1

        elif action == "decrement":
            new_quantity = int(splitted_call[-1]) - 1

            if new_quantity == 0:
                new_quantity = 1

        product_id = splitted_call[-2]
        await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=generate_product_menu(
                                                category_id=splitted_call[2],
                                                count=new_quantity,
                                                product_id=product_id)
                                            )

    elif splitted_call[0] == "add-to-cart":
        telegram_id = call.from_user.id
        user_id = get_user_id(telegram_id)
        categories = get_categories()
        product_id = splitted_call[-1]
        quantity = int(splitted_call[-2])

        try:
            add_to_cart(user_id=user_id,
                        product_id=product_id,
                        quantity=quantity)
            await bot.send_message(chat_id=call.from_user.id,
                                   text="Product has been successfully added to your cart")
        except:
            old_quantity = get_cart_product_quantity(
                user_id=user_id, product_id=product_id)
            update_product_quantity(
                new_quantity=old_quantity[0] + quantity, user_id=user_id, product_id=product_id)
            await bot.send_message(chat_id=call.from_user.id,
                                   text="Product's quantity has been successfully updated")

        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.message_id)

        with open(file="images/main_photo.jpeg", mode="rb") as photo:
            await bot.send_photo(
                chat_id=call.from_user.id,
                photo=photo,
                caption="📋 Main menu",
                reply_markup=generate_categories_menu(categories=categories)
            )


executor.start_polling(dispatcher=dp, skip_updates=True)

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


# Inline keyboard  => Attached to a message
# Reply keyboard   => Attached to bottom of a device

# Markup => Wrapper where we place our buttons
# Button => Individual button

def generate_main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.row(
        KeyboardButton("📋 Main menu"),
        KeyboardButton(text="📄 My orders")
    )
    keyboard.row(
        KeyboardButton(text="🛒 My cart"),
        KeyboardButton(text="🚚📦💵 Order")
    )

    return keyboard


def generate_categories_menu(categories):
    keyboard = InlineKeyboardMarkup()

    in_row = 2
    start = 0
    end = in_row
    rows = len(categories) // in_row

    if len(categories) % in_row != 0:
        rows += 1

    for _ in range(rows):
        buttons = []
        for category_id, category_name in categories[start:end]:
            buttons.append(
                InlineKeyboardButton(text=category_name, callback_data=f"category:{category_id}")  # "category:1"
            )
        keyboard.row(*buttons)
        start = end
        end += in_row

    return keyboard


def generate_category_products_menu(products):
    keyboard = InlineKeyboardMarkup()

    in_row = 2
    start = 0
    end = in_row
    rows = len(products) // in_row

    if len(products) % in_row != 0:
        rows += 1

    for _ in range(rows):
        buttons = []
        for product_id, category_id, product_name, price, description in products[start:end]:
            buttons.append(
                InlineKeyboardButton(text=product_name, callback_data=f"product:{product_id}")  # product:4
            )
        keyboard.row(*buttons)
        start = end
        end += in_row

    keyboard.row(
        InlineKeyboardButton(text="👈 Back", callback_data="back:categories"),
    )

    return keyboard


def generate_product_menu(category_id, product_id, count=1):
    markup = InlineKeyboardMarkup()

    markup.row(
        InlineKeyboardButton(
            text="-", callback_data=f"quantity:decrement:{category_id}:{product_id}:{count}"),
        InlineKeyboardButton(text=f"{count}", callback_data="..."),
        InlineKeyboardButton(
            text="+", callback_data=f"quantity:increment:{category_id}:{product_id}:{count}"),
    )
    markup.row(
        InlineKeyboardButton(text=f"🛒 Add to cart",
                             callback_data=f"add-to-cart:{count}:{product_id}")
    )
    markup.row(
        InlineKeyboardButton(
            text="👈 Back", callback_data=f"back:category:{category_id}")
    )

    return markup


def generate_pay_button(amount):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text=f"💳 Pay {amount} USD", callback_data="...")
    )

    return markup


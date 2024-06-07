from pymysql import connect

# In here, we will write function to create/retrieve/update/delete categories, products, ...

database = connect(
    database="railway",
    user="root",
    password="tbkCVpXPTHxsOEnAgyguwJqUufGmlBWX",
    host="roundhouse.proxy.rlwy.net",
    port=19164
)

cursor = database.cursor()


# To create categories table
def create_categories_table():
    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS categories(
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(20) UNIQUE
            );
        """
    )


# To create users table
def create_users_table():
    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS users(
                id INT PRIMARY KEY AUTO_INCREMENT,
                telegram_id VARCHAR(200) UNIQUE,
                full_name VARCHAR(200)
            );
        """
    )


# To create products table
def create_products_table():
    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS products(
                id INT PRIMARY KEY AUTO_INCREMENT,
                category_id INT NOT NULL,
                name VARCHAR(200) NOT NULL UNIQUE,
                price DECIMAL(5, 2) NOT NULL,
                description VARCHAR(255),

                CONSTRAINT check_price CHECK(price > 0)
            )
        """
    )


# To create user's cart table
def create_cart_table():
    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS cart(
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                total_price DECIMAL(12, 2),

                UNIQUE(user_id, product_id)
            )
        """
    )


# To create order_history table
def create_order_history_table():
    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS order_history(
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                total_price DECIMAL(12, 2) NOT NULL,
                created_datetime DATETIME NOT NULL
            )
        """
    )


# To clear user's cart products
def clean_users_cart(user_id):
    cursor.execute(
        """
            DELETE FROM cart WHERE user_id = %s
        """, (user_id,)
    )
    database.commit()


# To add products to orders history
def add_to_order_history(user_id, total_price, created_datetime, product_id):
    cursor.execute(
        """
            INSERT INTO order_history (user_id, total_price, created_datetime, product_id)
            VALUES (%s, %s, %s, %s)
        """, (user_id, total_price, created_datetime, product_id)
    )
    database.commit()


# To register user
def register_user(telegram_id, full_name):
    cursor.execute(
        """
            INSERT INTO users (telegram_id, full_name) 
            VALUES (%s, %s)
        """, (telegram_id, full_name)
    )
    database.commit()


# To add product to user's cart
def add_to_cart(user_id, product_id, quantity):
    product = get_product(product_id=product_id)
    product_price = product[-2]
    total_price = float(product_price) * int(quantity)

    cursor.execute(
        """
            INSERT INTO cart (user_id, product_id, quantity, total_price)
            VALUES (%s, %s, %s, %s)
        """, (user_id, product_id, quantity, total_price)
    )
    database.commit()


# To update product_quantity
def update_product_quantity(new_quantity, user_id, product_id):
    product = get_product(product_id=product_id)
    product_price = product[-2]
    total_price = float(product_price) * int(new_quantity)

    cursor.execute(
        """
            UPDATE cart SET quantity = %s, total_price = %s
            WHERE user_id = %s AND product_id = %s
        """, (new_quantity, total_price, user_id, product_id)
    )
    database.commit()


# To get user's cart
def get_cart(user_id):
    cursor.execute(
        """
            SELECT * FROM cart
            WHERE user_id = %s
        """, (user_id,)
    )
    cart_products = cursor.fetchall()
    return cart_products


# To get categories list
def get_categories():
    cursor.execute(
        """
            SELECT * FROM categories
        """
    )
    categories = cursor.fetchall()
    return categories


# To get prodcuts by soem category id
def get_category_products(category_id):
    cursor.execute(
        """
            SELECT * FROM products WHERE category_id = %s
        """, (category_id,)
    )
    products = cursor.fetchall()
    return products


# To get product
def get_product(product_id):
    cursor.execute(
        """
            SELECT * FROM products WHERE id = %s
        """, (product_id,)
    )
    product = cursor.fetchone()
    return product


# To get user's id by telegram id
def get_user_id(telegram_id):
    cursor.execute(
        """
            SELECT id FROM users WHERE telegram_id = %s
        """, (telegram_id,)
    )
    user_id = cursor.fetchone()
    return user_id


# To get user's product's quantity
def get_cart_product_quantity(user_id, product_id):
    cursor.execute(
        """
            SELECT quantity FROM cart WHERE user_id = %s AND product_id = %s
        """, (user_id, product_id)
    )
    quantity = cursor.fetchone()
    return quantity


# To get user's cart products
def get_users_products_in_cart(user_id):
    cursor.execute(
        """
            SELECT * FROM cart WHERE user_id = %s
        """, (user_id,)
    )
    products = cursor.fetchall()
    return products


# To get user's products from user's orders history
def get_users_order_history(user_id):
    cursor.execute(
        """
            SELECT * FROM order_history WHERE user_id = %s
        """, (user_id,)
    )
    return cursor.fetchall()

# To get user's cart's total amount
def get_users_cart_amount(user_id):
    cursor.execute(
        """
            SELECT SUM(total_price) FROM cart WHERE user_id = %s
        """, (user_id,)
    )
    total_price = cursor.fetchone()
    return total_price[0]


create_categories_table()
create_users_table()
create_products_table()
create_cart_table()
create_order_history_table()


from flask import Flask, render_template, request, redirect, url_for, flash

from models import (
    add_product,
    get_total_products,
    get_total_stock,
    get_total_inventory_value,
    get_low_stock,
    get_all_products,
    get_product_by_id,
    update_product,
    delete_product,
    search_products,
    get_categories,
    filter_products
)

app = Flask(__name__)
app.secret_key = "inventory-management-local-key"


def validate_product_form():
    product_name = request.form.get("product_name", "").strip()
    category = request.form.get("category", "").strip()
    price_input = request.form.get("price", "").strip()
    print("PRICE RECEIVED:", repr(price_input))
    quantity_input = request.form.get("quantity", "").strip()
    supplier = request.form.get("supplier", "").strip()

    if not product_name or not category or not supplier:
        return None, "Product name, category, and supplier are required."

    try:
        price = float(price_input)

        if price < 0.001:
            return None, "Price must be at least ₹0.001."

    except (ValueError, TypeError):
        return None, "Enter a valid price of at least ₹0.001."

    try:
        if not quantity_input or not quantity_input.isdigit():
            return None, "Quantity must be a whole number of 0 or greater."

        quantity = int(quantity_input)
    except (ValueError, TypeError):
        return None, "Enter a valid whole-number quantity."

    return {
        "product_name": product_name,
        "category": category,
        "price": price,
        "quantity": quantity,
        "supplier": supplier
    }, None


@app.route("/")
def home():
    total_products = get_total_products()
    total_stock = get_total_stock()
    low_stock = get_low_stock()
    total_inventory_value = get_total_inventory_value()

    return render_template(
        "index.html",
        total_products=total_products,
        total_stock=total_stock,
        low_stock=low_stock,
        total_inventory_value=total_inventory_value
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        product, error = validate_product_form()

        if error:
            flash(error, "error")
            return render_template("add_product.html")

        add_product(
            product["product_name"],
            product["category"],
            product["price"],
            product["quantity"],
            product["supplier"]
        )

        flash("Product added successfully!", "success")
        return redirect(url_for("products"))

    return render_template("add_product.html")


@app.route("/products")
def products():
    keyword = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    if keyword:
        products = search_products(keyword)
    elif category:
        products = filter_products(category)
    else:
        products = get_all_products()

    categories = get_categories()

    return render_template(
        "products.html",
        products=products,
        categories=categories,
        selected_category=category
    )


@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if request.method == "POST":
        product, error = validate_product_form()

        if error:
            flash(error, "error")
            current_product = get_product_by_id(product_id)

            return render_template(
                "edit_product.html",
                product=current_product
            )

        update_product(
            product_id,
            product["product_name"],
            product["category"],
            product["price"],
            product["quantity"],
            product["supplier"]
        )

        flash("Product updated successfully!", "success")
        return redirect(url_for("products"))

    product = get_product_by_id(product_id)

    return render_template(
        "edit_product.html",
        product=product
    )


@app.route("/delete/<int:product_id>", methods=["POST"])
def delete(product_id):
    delete_product(product_id)
    flash("Product deleted successfully!", "success")
    return redirect(url_for("products"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
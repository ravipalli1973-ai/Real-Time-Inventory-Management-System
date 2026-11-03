import os
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
app.secret_key = os.environ.get("SECRET_KEY", "inventory-management-local-key")


def validate_product_form():
    """Validates and extracts product form fields from request.form."""
    product_name = request.form.get("product_name", "").strip()
    category = request.form.get("category", "").strip()
    price_input = request.form.get("price", "").strip()
    quantity_input = request.form.get("quantity", "").strip()
    supplier = request.form.get("supplier", "").strip()

    raw_data = {
        "product_name": product_name,
        "category": category,
        "price": price_input,
        "quantity": quantity_input,
        "supplier": supplier
    }

    if not product_name or not category or not supplier:
        return None, "Product name, category, and supplier are required.", raw_data

    try:
        price = float(price_input)
        if price < 0.001:
            return None, "Price must be at least ₹0.001.", raw_data
    except (ValueError, TypeError):
        return None, "Enter a valid price of at least ₹0.001.", raw_data

    try:
        quantity = int(quantity_input)
        if quantity < 0:
            return None, "Quantity must be a whole number of 0 or greater.", raw_data
    except (ValueError, TypeError):
        return None, "Enter a valid whole-number quantity of 0 or greater.", raw_data

    validated_product = {
        "product_name": product_name,
        "category": category,
        "price": price,
        "quantity": quantity,
        "supplier": supplier
    }
    return validated_product, None, raw_data


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
    categories = get_categories()

    if request.method == "POST":
        product, error, form_data = validate_product_form()

        if error:
            flash(error, "error")
            return render_template(
                "add_product.html",
                product=form_data,
                categories=categories
            )

        add_product(
            product["product_name"],
            product["category"],
            product["price"],
            product["quantity"],
            product["supplier"]
        )

        flash("Product added successfully!", "success")
        return redirect(url_for("products"))

    return render_template("add_product.html", product={}, categories=categories)


@app.route("/products")
def products():
    keyword = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    if keyword:
        product_list = search_products(keyword)
    elif category:
        product_list = filter_products(category)
    else:
        product_list = get_all_products()

    categories = get_categories()

    return render_template(
        "products.html",
        products=product_list,
        categories=categories,
        selected_category=category,
        search_query=keyword
    )


@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("products"))

    categories = get_categories()

    if request.method == "POST":
        validated_product, error, form_data = validate_product_form()

        if error:
            flash(error, "error")
            # Preserve user input and product_id on validation failure
            form_data["id"] = product_id
            return render_template(
                "edit_product.html",
                product=form_data,
                categories=categories
            )

        update_product(
            product_id,
            validated_product["product_name"],
            validated_product["category"],
            validated_product["price"],
            validated_product["quantity"],
            validated_product["supplier"]
        )

        flash("Product updated successfully!", "success")
        return redirect(url_for("products"))

    return render_template(
        "edit_product.html",
        product=product,
        categories=categories
    )


@app.route("/delete/<int:product_id>", methods=["POST"])
def delete(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash("Product does not exist or has already been removed.", "error")
        return redirect(url_for("products"))

    delete_product(product_id)
    flash("Product deleted successfully!", "success")
    return redirect(url_for("products"))


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("home"))


@app.errorhandler(500)
def internal_server_error(e):
    flash("An unexpected server error occurred. Please try again.", "error")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(
        host=os.environ.get("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.environ.get("FLASK_RUN_PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    )

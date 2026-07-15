
from flask import Flask, render_template, request, redirect, url_for
from models import (
    add_product,
    get_total_products,
    get_total_stock,
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


@app.route("/")
def home():
    total_products = get_total_products()
    total_stock = get_total_stock()
    low_stock = get_low_stock()

    return render_template(
        "index.html",
        total_products=total_products,
        total_stock=total_stock,
        low_stock=low_stock
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        product_name = request.form["product_name"]
        category = request.form["category"]
        price = request.form["price"]
        quantity = request.form["quantity"]
        supplier = request.form["supplier"]

        add_product(
            product_name,
            category,
            price,
            quantity,
            supplier
        )

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

        product_name = request.form["product_name"]
        category = request.form["category"]
        price = request.form["price"]
        quantity = request.form["quantity"]
        supplier = request.form["supplier"]

        update_product(
            product_id,
            product_name,
            category,
            price,
            quantity,
            supplier
        )

        return redirect(url_for("products"))

    product = get_product_by_id(product_id)

    return render_template(
        "edit_product.html",
        product=product
    )


@app.route("/delete/<int:product_id>")
def delete(product_id):
    delete_product(product_id)
    return redirect(url_for("products"))
if __name__ == "__main__":
    app.run(debug=True)



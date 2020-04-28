from flask import render_template, session, redirect, url_for, request
from app import app, db
from app.models import Product, Order, CartItem, Category
from app.forms import AddToCart, OrderForm, SearchForm
from sqlalchemy import or_

@app.route('/')
def index():
    products = Product.query.all()
    categories = Category.query.all()

    return render_template('index.html', products=products, categories=categories)

@app.route('/product/<string:id>', methods=('GET', 'POST'))
def product(id):    

    if 'cart' not in session:
        session['cart'] = {}

    product = Product.query.filter_by(id=id).first()
    form = AddToCart()
    print(session['cart'])
    if form.validate_on_submit():
        if id in session['cart']:
            session['cart'][id]['quantity'] += form.data['quantity']
        else:
            session['cart'][id] = {'quantity': form.data['quantity']}
        
        session.modified = True

        return redirect(url_for('cart_list')) 

    return render_template('product.html', product=product, form=form)

@app.route('/cart', methods=('GET', 'POST'))
def cart_list():
    products = []
    form = AddToCart()
    print(session['cart'])

    if session['cart']:
        for key, value in session['cart'].items():
            product = Product.query.filter_by(id=key).first()
            products.append({
                'id': key,
                'item': product.name,
                'quantity': value['quantity']
            })
    
    if form.validate_on_submit():
        session['cart'][form.data['id']] = {'quantity': form.data['quantity']}
        session.modified = True

        return redirect(url_for('cart_list'))

    return render_template('cart.html', products=products, form=form)

@app.route('/remove-cart/<string:id>')
def remove_from_cart(id):
    del session['cart'][id]
    session.modified = True

    return redirect(url_for('cart_list'))


@app.route('/order', methods=('GET', 'POST'))
def order():
    """
    Create an ORDER form
    After ORDER form is submitted, create it in the database
    Next, loop over cart and make a CartItem for each item. 
    This will create an Order that contains many order items
    You can then access an Order and query the CartItems directly.
    On successful completion of an order, flash a success message
    """
    form = OrderForm()
    
    if form.validate_on_submit():
        order = Order(
            first_name=form.data['first_name'],
            last_name=form.data['last_name'],
            email=form.data['email'],
            address=form.data['address'],
            postal_code=form.data['postal_code'],
            city=form.data['city']
        )
        order.save()

        for key, value in session['cart'].items():
            product = Product.query.filter_by(id=key).first()
            cart_item_to_order = CartItem(
                                product_id=product.id,
                                order_id=order.id,
                                quantity=value['quantity']
                                )
            cart_item_to_order.save()

            return redirect(url_for('index'))

    return render_template('order.html', form=form)

@app.route('/search', defaults={'category': None})
@app.route('/search/<string:category>')
def search(category):    
    filtered_results = None
    query = request.args
    search_results = None
    category_types = [category_entry.name for category_entry in Category.query.all()]
    category_search = Category.query.filter_by(name=category).first()
    page = request.args.get('page', 1, type=int)

    # Filter for any number of parameters given

    filter_array = ['price', 'size', 'color']

    for v in filter_array:
        if v == 'price' and query.getlist(v):
            price = int(query.getlist(v)[0])
            filtered_results = Product.query.filter(Product.price.between((price - 100), price))

        elif query.getlist(v):
            if not filtered_results:
                filtered_results = Product.query.filter(getattr(Product, v).in_(query.getlist(v)))
                if category_search:
                    filtered_results = filtered_results.filter_by(product_category=category_search)
            else:
                filtered_results = filtered_results.filter(getattr(Product, v).in_(query.getlist(v)))

    if filtered_results is not None:
        # Return items with given filtered params
        search_results = filtered_results.paginate(page, 2, False)
    elif category_search:
        # Return all products for the given category
        search_results = Product.query.filter_by(product_category=category_search).paginate(page, 2, False)
    else:
        # No category given: return all products
        search_results = Product.query.paginate(page, 3, False)

    form = SearchForm()
    # Currently, urls dont take in params so prev and next are incorrect if filters are applied
    url_prev = url_for('search', page=search_results.prev_num, category=category) if search_results.has_prev else None
    url_next = url_for('search', page=search_results.next_num, category=category) if search_results.has_next else None
    
    return render_template('search.html',  
                            search_results=search_results.items, 
                            category=category, 
                            category_types=category_types, 
                            form=form,
                            url_next=url_next,
                            url_prev=url_prev
                        )

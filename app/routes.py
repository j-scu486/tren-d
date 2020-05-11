from flask import render_template, session, redirect, url_for, request, flash
from app import app, db, r
from app.models import Product, Order, CartItem, Category
from app.forms import AddToCart, OrderForm, SearchForm
from app.search import SearchItems

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
    cart_product = None
    form = AddToCart()
    
    # List most popular items
    product_ranking = r.zrange('product_ranking', 0, -1, desc=True)[:3]
    product_ranking_ids = [int(id) for id in product_ranking]

    most_popular = list(Product.query.filter(Product.id.in_(product_ranking_ids)))
    most_popular.sort(key=lambda x: product_ranking_ids.index(x.id))

    # Add item to cart

    if form.validate_on_submit():
        try:
            cart_product = Product.query.filter_by(size=form.data['size'],name=product.name).first()
            
            if cart_product is None:
                raise Exception("We're sorry, but that size is currently out of stock")
            elif form.data['quantity'] > cart_product.stock:
                raise Exception("We're sorry, but we do not have that much in stock!")

        except Exception as e:
            # Flash message that product is not available for whatever reason
            flash(str(e))
            return redirect(url_for('product', id=product.id))

        cart_product_id = str(cart_product.id)

        if cart_product_id in session['cart']:
            session['cart'][cart_product_id]['quantity'] += form.data['quantity']
        else:
            session['cart'][cart_product_id] = {'quantity': form.data['quantity']}
        
        session.modified = True
        
        return redirect(url_for('cart_list')) 

    return render_template('product.html', product=product, form=form, most_popular=most_popular)

@app.route('/cart', methods=('GET', 'POST'))
def cart_list():
    products = []
    cart_product = None
    total = 0

    if session['cart']:
        for key, value in session['cart'].items():
            product = Product.query.filter_by(id=key).first()
            products.append({
                'id': key,
                'item': product.name,
                'size': product.size,
                'quantity': value['quantity'],
                'price': product.price,
                'subtotal': (product.price * value['quantity']),
                'image_url': product.image_url
            })

            total += product.price * value['quantity']

    total_tax = round(total + (total * 0.1))
    form = AddToCart()

    if form.validate_on_submit():
        # This needs to be validated as above to make sure that someone doesnt purchase over the stock limit
        try:
            cart_product = Product.query.filter_by(size=form.data['size'], name=form.data['name']).first()
            
            if cart_product is None:
                raise Exception("We're sorry, but that size is currently out of stock")
            elif form.data['quantity'] > cart_product.stock:
                raise Exception("We're sorry, but we do not have that much in stock!")

        except Exception as e:
            # Flash message that product is not available for whatever reason
            flash(str(e))
            return redirect(url_for('cart_list'))

        cart_product_id = str(cart_product.id)

        # Different size was selected, so delete the original from session
        if cart_product_id != form.data['id']:
            del session['cart'][form.data['id']]

        session['cart'][cart_product_id] = {'quantity': form.data['quantity']}
        session.modified = True

        return redirect(url_for('cart_list'))
    return render_template('cart.html', products=products, form=form, total_tax=total_tax, total=total)

def cart_length():
    return len(session['cart'])

@app.route('/remove-cart/<string:id>')
def remove_from_cart(id):
    del session['cart'][id]
    session.modified = True

    return redirect(url_for('cart_list'))

@app.route('/search', defaults={'category': None})
@app.route('/search/<string:category>')
def search(category):    
    query = request.args
    search_results = None
    category_types = [category_entry.name for category_entry in Category.query.all()]
    category_search = Category.query.filter_by(name=category).first()
    url_kwargs = {}
    page = request.args.get('page', 1, type=int)

    # Save search preferences    
    if request.args.get('show'):
        session['search'] = request.args.get('show', type=int)

    if request.args.get('sort'):
        session['sort'] = request.args.get('sort', type=str)
    
    search = SearchItems(['price', 'size', 'color'], category_search, query, page)
    if 'sort' in session:
        search_results = search.get_sorted_results(session['sort'])    
    else: 
        search_results = search.get_results()

    url_kwargs = search.get_url_kwargs()
    form = SearchForm()

    url_prev = url_for('search', page=search_results.prev_num, category=category, **url_kwargs) if search_results.has_prev else None
    url_next = url_for('search', page=search_results.next_num, category=category, **url_kwargs) if search_results.has_next else None
    
    return render_template('search.html',  
                            search_results=search_results.items, 
                            category=category, 
                            category_types=category_types, 
                            form=form,
                            url_next=url_next,
                            url_prev=url_prev
                        )



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
    products = []

    if session['cart']:
        for key, value in session['cart'].items():
            product = Product.query.filter_by(id=key).first()
            products.append({
                'id': key,
                'item': product.name,
                'quantity': value['quantity'],
                'price': product.price,
                'subtotal': (product.price * value['quantity']),
                'image_url': product.image_url
            })

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

        return redirect(url_for('order_confirm', id=order.id))

    return render_template('order.html', form=form, products=products)

"""
    Route for confirming order.
    Accepts the order ID in url params.
    In this route, add cart items to order and mark order as paid if successful.
    Provide option to cancel, which will delete order item (but still keep cart)
    
"""

@app.route('/order/<string:id>', methods=('GET', 'POST'))
def order_confirm(id):
    
    order = Order.query.filter_by(id=id).first()
    products = []

    if session['cart']:
        for key, value in session['cart'].items():
            product = Product.query.filter_by(id=key).first()
            products.append({
                'id': key,
                'item': product.name,
                'quantity': value['quantity'],
                'price': product.price,
                'subtotal': (product.price * value['quantity']),
                'image_url': product.image_url
            })

    if order is None:
        return redirect(url_for('cart_list'))

    if request.method == 'POST':    
        for key, value in session['cart'].items():
            product = Product.query.filter_by(id=key).first()
            cart_item_to_order = CartItem(
                                product_id=product.id,
                                order_id=order.id,
                                quantity=value['quantity']
                                )
            # Save items to the order
            cart_item_to_order.save()
            # Mark the order as paid
            order.mark_paid()
            # Find products and reduce their stock accordingly
            product.reduce_qty(value['quantity'])
            # Increment redis total purchased amount
            total_purchased = r.incr('product:{}:purchased'.format(product.id))
            # Increment rankings
            r.zincrby('product_ranking', 1, product.id)
            # Clear Cart
            session['cart'] = {}
            

            return redirect(url_for('thanks'))

    return render_template('order_confirm.html', products=products, order=order)

@app.route('/order-confirmed')
def thanks():
    return render_template('order_thanks.html')

@app.route('/redis')
def test():
    
    return 'Success'
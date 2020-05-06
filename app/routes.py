from flask import render_template, session, redirect, url_for, request, flash
from app import app, db
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

    return render_template('product.html', product=product, form=form)

@app.route('/cart', methods=('GET', 'POST'))
def cart_list():
    products = []
    cart_product = None

    if session['cart']:
        for key, value in session['cart'].items():
            product = Product.query.filter_by(id=key).first()
            products.append({
                'id': key,
                'item': product.name,
                'size': product.size,
                'quantity': value['quantity'],
                'price': (product.price * value['quantity']),
                'image_url': product.image_url
            })

    form = AddToCart(size=0)
    
    if form.validate_on_submit():
        # This needs to be validated as above to make sure that someone doesnt purchase over the stock limit
        try:
            cart_product = Product.query.filter_by(size=form.data['size'],name=product.name).first()
            
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
    query = request.args
    search_results = None
    category_types = [category_entry.name for category_entry in Category.query.all()]
    category_search = Category.query.filter_by(name=category).first()
    url_kwargs = {}
    page = request.args.get('page', 1, type=int)

    # Save search preferences
    if request.args.get('show'):
        session['search'] = request.args.get('show', type=int)
    else:
        session['search'] = 9
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

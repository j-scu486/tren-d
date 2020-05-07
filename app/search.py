from app.models import Product
from flask import session

class SearchItems(object):
    def __init__(self, filter_list, category, query, page):
        self.filter_list = filter_list
        self.category = category
        self.query = query
        self.page = page
        self.url_kwargs = {}
        self.show_num_pages = session['search'] if 'search' in session else 9

    def filter(self):
        filtered_results = None

        for v in self.filter_list:
            if v == 'price' and self.query.getlist(v):
                price = int(self.query.getlist(v)[0])
                filtered_results = Product.query.filter(Product.price.between((price - 100), price))
                if self.category:
                    filtered_results = filtered_results.filter_by(product_category=self.category)

            elif self.query.getlist(v):
                if not filtered_results:
                    filtered_results = Product.query.filter(getattr(Product, v).in_(self.query.getlist(v)))
                    if self.category:
                        filtered_results = filtered_results.filter_by(product_category=self.category)
                else:
                    filtered_results = filtered_results.filter(getattr(Product, v).in_(self.query.getlist(v)))
                
            self.url_kwargs[v] = self.query.getlist(v)

        if filtered_results:
            return filtered_results
        elif filtered_results is None and self.category:

            return Product.query.filter_by(product_category=self.category)
        else:
            return Product.query

    def get_url_kwargs(self):
        return self.url_kwargs

    def get_results(self, sorted_results=None):
        results = sorted_results if sorted_results else self.filter()

        return results.group_by(Product.name).paginate(self.page, self.show_num_pages, False)

    def get_sorted_results(self, sort_type):
        results = self.filter()
        sorted_results = None

        if sort_type == 'asc':
            sorted_results = results.order_by(Product.price.asc())
        elif sort_type == 'desc':
            sorted_results = results.order_by(Product.price.desc())

        return self.get_results(sorted_results)
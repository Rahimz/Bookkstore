from django.shortcuts import get_object_or_404

from .models import Product


def has_empty_price_row(product, variation):
    # variations = {
    #     'new':{
    #         product.price: product.stock,
    #         product.price_1: product.stock_1,
    #     },
    #     'used':{
    #     product.price_used: product.stock_used,
    #     }
    # }
    variations = {
        'new':{
            'main':{
                'price': product.price,
                 'stock': product.stock,
            },
            'v1':{
                'price': product.price_1,
                'stock': product.stock_1,
            },
        },
        'used':{
            'main':{
                'price': product.price_used,
                'stock': product.stock_used,
            }
        }
    }
    result = None
    for key in variations.keys():
        # print(key, item)
        for i in variations[key].keys():
            if variations[variation][i]['price'] == 0:
                result = i
                return i
    return result

def add_price(price, stock, variation, product_id):
    product = get_object_or_404(Product, pk=product_id)
    # print(price, stock, variation, product_id)
    # print( has_empty_price_row(product, variation))
    variations = {
        'new':{
            'main':{
                'price': product.price,
                 'stock': product.stock,
            },
            'v1':{
                'price': product.price_1,
                'stock': product.stock_1,
            },
        },
        'used':{
            'main':{
                'price': product.price_used,
                'stock': product.stock_used,
            }
        }
    }


    new_var = has_empty_price_row(product, variation)
    if variation == 'new':
        if new_var == 'main':
            product.price = price
            product.stock = stock
            # print(variation, new_var, price)

        elif new_var == 'v1':
            product.price_1 = price
            product.stock_1 = stock
            # print(variation, new_var, price)


    elif variation == 'used':
        if new_var == 'main':
            product.price_used = price
            product.stock_used = stock
            # print(variation, new_var, price)


    product.has_other_prices = True
    product.save()


def sort_price(product_id):
    pass

def find_empty_price_row(product):
    pass

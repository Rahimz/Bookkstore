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

    for key in variations.keys():
        # print("Has empty price row", key,)
        for i in variations[key].keys():
            if variations[variation][i]['price'] == 0:
                # print('the row that is empty: ', f"{variation} {i}")
                return i
    return None

def sort_price(product):
    p1, s1 = product.price, product.stock
    p2, s2 = product.price_1, product.stock_1
    prices = [(p1, s1), (p2, s2)]

    prices.sort(key=lambda x : x[0], reverse=True)

    product.price = prices[0][0]
    product.stock = prices[0][1]

    product.price_1 = prices[1][0]
    product.stock_1 = prices[1][1]

    product.save()


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
    print('new_var', new_var)
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

    sort_price(product)

def get_price_index(product_id, variation, price):
    product = get_object_or_404(Product, pk=product_id)
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
    print(variations[variation])
    for i in variations[variation].keys():
        print(variation, i, variations[variation][i], price)

        if variations[variation][i]['price'] == price:
            return i

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
            'v2':{
                'price': product.price_2,
                'stock': product.stock_2,
            },
            'v3':{
                'price': product.price_3,
                'stock': product.stock_3,
            },
            'v4':{
                'price': product.price_4,
                'stock': product.stock_4,
            },
            'v5':{
                'price': product.price_5,
                'stock': product.stock_5,
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
    p0, s0 = product.price, product.stock
    p1, s1 = product.price_1, product.stock_1
    p2, s2 = product.price_2, product.stock_2
    p3, s3 = product.price_3, product.stock_3
    p4, s4 = product.price_4, product.stock_4
    p5, s5 = product.price_5, product.stock_5
    prices = [(p0, s0), (p1, s1), (p2, s2), (p3, s3), (p4, s4), (p5, s5),]

    prices.sort(key=lambda x : x[0], reverse=True)

    product.price = prices[0][0]
    product.stock = prices[0][1]

    product.price_1 = prices[1][0]
    product.stock_1 = prices[1][1]

    product.price_2 = prices[2][0]
    product.stock_2 = prices[2][1]

    product.price_3 = prices[3][0]
    product.stock_3 = prices[3][1]

    product.price_4 = prices[4][0]
    product.stock_4 = prices[4][1]

    product.price_5 = prices[5][0]
    product.stock_5 = prices[5][1]

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
            'v2':{
                'price': product.price_2,
                'stock': product.stock_2,
            },
            'v3':{
                'price': product.price_3,
                'stock': product.stock_3,
            },
            'v4':{
                'price': product.price_4,
                'stock': product.stock_4,
            },
            'v5':{
                'price': product.price_5,
                'stock': product.stock_5,
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


        elif new_var == 'v1':
            product.price_1 = price
            product.stock_1 = stock
        elif new_var == 'v2':
            product.price_2 = price
            product.stock_2 = stock
        elif new_var == 'v3':
            product.price_3 = price
            product.stock_3 = stock
        elif new_var == 'v4':
            product.price_4 = price
            product.stock_4 = stock
        elif new_var == 'v5':
            product.price_5 = price
            product.stock_5 = stock



    elif variation == 'used':
        if new_var == 'main':
            product.price_used = price
            product.stock_used = stock



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
            'v2':{
                'price': product.price_2,
                'stock': product.stock_2,
            },
            'v3':{
                'price': product.price_3,
                'stock': product.stock_3,
            },
            'v4':{
                'price': product.price_4,
                'stock': product.stock_4,
            },
            'v5':{
                'price': product.price_5,
                'stock': product.stock_5,
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

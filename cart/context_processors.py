from .cart import Cart


# Creat context processor so our cart can work an all pages
def cart(request):
    # Return the default data from our Cart
    return {"cart": Cart(request)}


import json
from django.utils import timezone

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q

from .models import Product, Category, Profile, ProductPopularity, ProductRating
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingAddressForm
from payment.models import ShippingAddress
from cart.cart import Cart


def search(request):
    if request.method == 'POST':
        searched = request.POST.get('searched', '')
        products = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        if not products.exists():
            messages.info(request, 'No products found or that product does not exist. Please try again.')
            return render(request, "search.html")
        return render(request, "search.html", {"searched": products})
    return render(request, "search.html")


def update_info(request):
    if request.user.is_authenticated:
        try:
            current_user = Profile.objects.get(user=request.user)
            shipping_user = ShippingAddress.objects.get(user=request.user)
        except ObjectDoesNotExist:
            messages.error(request, 'User profile or shipping address not found.')
            return redirect('home')

        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_form = ShippingAddressForm(request.POST or None, instance=shipping_user)

        if form.is_valid() and shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request, 'Your info has been updated!')
            return redirect('home')
        return render(request, 'update_info.html', {'form': form, 'shipping_form': shipping_form})
    messages.error(request, 'You are not logged in.')
    return redirect('home')


def update_password(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ChangePasswordForm(user=request.user, data=request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been updated!')
                login(request, request.user)
                return redirect('update_password')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
        else:
            form = ChangePasswordForm(user=request.user)
        return render(request, 'update_password.html', {'form': form})
    messages.error(request, 'You must be logged in to view that page.')
    return redirect('home')


def category_summary(request):
    categories = Category.objects.all()
    return render(request, "category_summary.html", {"categories": categories})


def category_(request, foo):
    foo = foo.replace('-', ' ')
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, "category.html", {'products': products, "category": category})
    except ObjectDoesNotExist:
        messages.error(request, 'That category does not exist.')
        return redirect('home')


def product_viewed(request, pk):
    try:
        product = Product.objects.get(id=pk)
        popularity, created = ProductPopularity.objects.get_or_create(product=product)
        popularity.view_count += 1
        popularity.last_viewed = timezone.now()
        popularity.save()

        # Retrieve rating
        rating = ProductRating.objects.filter(product=product).first()  # Get the first rating if available

        stars = [1, 2, 3, 4, 5]

        return render(request, "product.html", {"product": product, "rating": rating, "stars": stars})
    except ObjectDoesNotExist:
        messages.error(request, 'Product not found.')
        return redirect('home')


def product_purchased(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        popularity, created = ProductPopularity.objects.get_or_create(product=product)
        popularity.purchase_count += 1
        popularity.save()
    except ObjectDoesNotExist:
        messages.error(request, 'Product not found.')


def rate_product(request, pk):
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=pk)
            rating = request.POST.get('rating')
            if rating:
                rating = int(rating)
                # Зберегти рейтинг
                ProductRating.objects.update_or_create(product=product, defaults={'rating': rating})
                return JsonResponse({'success': True})
        except ObjectDoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def update_user(request):
    if request.user.is_authenticated:
        user_form = UpdateUserForm(request.POST or None, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            login(request, request.user)
            messages.success(request, 'Your account has been updated!')
            return redirect('home')
        return render(request, 'update_user.html', {'user_form': user_form})
    messages.error(request, 'You are not logged in.')
    return redirect('home')


def home(request):
    products = Product.objects.all()
    return render(request, "home.html", {"products": products})


def about(request):
    return render(request, "about.html")


def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                current_user = Profile.objects.get(user=request.user)
                saved_cart = current_user.old_cart
                if saved_cart:
                    converted_cart = json.loads(saved_cart)
                    cart = Cart(request)
                    for key, value in converted_cart.items():
                        cart.db_add(product=key, quantity=value)
            except ObjectDoesNotExist:
                messages.error(request, 'User profile not found.')
            messages.success(request, 'You are now logged in.')
            return redirect("home")
        messages.error(request, 'Incorrect username or password.')
        return redirect("login")
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect("home")


def register_user(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'You have registered.')
            return redirect('update_info')
        messages.error(request, 'There is already a user with that username.')
    return render(request, 'register.html', {"form": form})

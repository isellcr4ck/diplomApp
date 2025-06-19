from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Currency, Cart, CartItem, Transaction, Review  # Django ORM models, .objects is correct
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, ReviewForm, FeedbackForm
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.http import require_POST

def index(request):
    from .models import Review
    random_reviews = Review.objects.filter(is_published=True).order_by('?')[:3]
    return render(request, 'index.html', {'random_reviews': random_reviews})

def catalog(request):
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'name-asc')
    currencies = Currency.objects.all()
    if query:
        currencies = currencies.filter(name__icontains=query) | currencies.filter(code__icontains=query)
    # Сортировка
    if sort == 'name-asc':
        currencies = currencies.order_by('name')
    elif sort == 'name-desc':
        currencies = currencies.order_by('-name')
    elif sort == 'rate-asc':
        currencies = currencies.order_by('buy_rate')
    elif sort == 'rate-desc':
        currencies = currencies.order_by('-buy_rate')
    # Логика обмена валют через форму
    if request.method == 'POST' and request.user.is_authenticated:
        from_currency_id = request.POST.get('from_currency')
        to_currency_id = request.POST.get('to_currency')
        amount = request.POST.get('amount')
        # Проверка на пустые или одинаковые валюты
        if not from_currency_id or not to_currency_id or from_currency_id == to_currency_id:
            messages.error(request, 'Выберите разные валюты для обмена!')
            return redirect('catalog')
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            messages.error(request, 'Некорректная сумма')
            return redirect('catalog')
        from_currency = Currency.objects.get(id=from_currency_id)
        to_currency = Currency.objects.get(id=to_currency_id)
        # Проверка баланса пользователя по валюте, которую он отдаёт
        user_transactions = Transaction.objects.filter(user=request.user, currency=from_currency, status='completed')
        balance = 0.0
        for t in user_transactions:
            if t.operation_type == 'buy':
                balance += float(t.amount)
            elif t.operation_type == 'sell':
                balance -= float(t.amount)
        # Учитываем ещё не завершённые обмены в корзине
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if cart:
            cart_items = CartItem.objects.filter(cart=cart, currency=from_currency, operation_type='sell')
            for item in cart_items:
                balance -= float(item.amount)
        if amount > balance:
            messages.error(request, f'Недостаточно {from_currency.code} для обмена. Ваш баланс: {balance:.2f}')
            return redirect('catalog')
        # Считаем сколько получит пользователь
        receive_amount = amount * float(from_currency.sell_rate) / float(to_currency.buy_rate)
        # Передаём параметры в add_to_cart для создания двух операций (sell и buy)
        return redirect(f'/cart/add/{from_currency.id}/?amount={amount}&operation_type=sell&to_currency={to_currency.id}&receive_amount={receive_amount}')
    currencies_json = json.dumps(
        list(currencies.values('id', 'code', 'name', 'buy_rate', 'sell_rate')),
        cls=DjangoJSONEncoder
    )
    return render(request, 'catalog.html', {'currencies': currencies, 'currencies_json': currencies_json, 'query': query, 'sort': sort})

def contacts(request):
    form = FeedbackForm(request.POST or None)
    sent = False
    if request.method == 'POST' and form.is_valid():
        form.save()
        sent = True
        messages.success(request, 'Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.')
        form = FeedbackForm()  # очистить форму
    return render(request, 'contacts.html', {'form': form, 'sent': sent})

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            Cart.objects.create(user=user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('account')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('account')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def account_view(request):
    user = request.user
    cart = Cart.objects.filter(user=user, is_active=True).first()
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:10]
    # Универсальный расчет баланса по всем валютам
    balance = {}
    for t in Transaction.objects.filter(user=user, status='completed'):
        code = t.currency.code
        if code not in balance:
            balance[code] = 0.0
        if t.operation_type == 'buy':
            balance[code] += float(t.amount)
        elif t.operation_type == 'sell':
            balance[code] -= float(t.amount)
    # Подсчёт общего баланса в рублях
    total_rub = 0.0
    for code, amount in balance.items():
        if code == 'RUB':
            total_rub += amount
        else:
            try:
                currency = Currency.objects.get(code=code)
                total_rub += float(amount) * float(currency.sell_rate)
            except Currency.DoesNotExist:
                pass
    # Получаем список всех валют (или только популярных)
    currencies = Currency.objects.all()
    return render(request, 'account.html', {
        'user': user,
        'cart': cart,
        'transactions': transactions,
        'balance': balance,
        'total_rub': total_rub,
        'currencies': currencies,
    })

@login_required
def add_to_cart(request, currency_id):
    currency = get_object_or_404(Currency, id=currency_id)
    active_carts = Cart.objects.filter(user=request.user, is_active=True).order_by('-created_at')
    if active_carts.count() > 1:
        for cart in active_carts[1:]:
            cart.is_active = False
            cart.save()
    cart = active_carts.first() if active_carts.exists() else Cart.objects.create(user=request.user, is_active=True)
    amount = request.POST.get('amount') or request.GET.get('amount')
    operation_type = request.POST.get('operation_type') or request.GET.get('operation_type')
    to_currency_id = request.POST.get('to_currency') or request.GET.get('to_currency')
    receive_amount = request.POST.get('receive_amount') or request.GET.get('receive_amount')
    if request.method == 'POST' or (amount and operation_type):
        try:
            amount = float(amount)
            receive_amount = float(receive_amount) if receive_amount else None
        except (TypeError, ValueError):
            messages.error(request, 'Некорректная сумма')
            return redirect('catalog')
        # Если это обмен (operation_type == 'sell' и есть to_currency и receive_amount)
        if operation_type == 'sell' and to_currency_id and receive_amount:
            to_currency = Currency.objects.get(id=to_currency_id)
            # Проверка баланса уже была в catalog, здесь просто создаём две записи в корзине
            CartItem.objects.create(
                cart=cart,
                currency=currency,
                amount=amount,
                operation_type='sell',
                rate=currency.sell_rate
            )
            CartItem.objects.create(
                cart=cart,
                currency=to_currency,
                amount=receive_amount,
                operation_type='buy',
                rate=to_currency.buy_rate
            )
            messages.success(request, f'Обмен добавлен в корзину: {amount} {currency.code} → {receive_amount:.2f} {to_currency.code}')
            return redirect('cart')
        # Старый режим (например, покупка/продажа одной валюты)
        if operation_type == 'sell':
            user_transactions = Transaction.objects.filter(user=request.user, currency=currency, status='completed')
            balance = 0.0
            for t in user_transactions:
                if t.operation_type == 'buy':
                    balance += float(t.amount)
                elif t.operation_type == 'sell':
                    balance -= float(t.amount)
            cart_items = CartItem.objects.filter(cart=cart, currency=currency, operation_type='sell')
            for item in cart_items:
                balance -= float(item.amount)
            if amount > balance:
                messages.error(request, f'Недостаточно {currency.code} для продажи. Ваш баланс: {balance:.2f}')
                return redirect('catalog')
        rate = currency.buy_rate if operation_type == 'buy' else currency.sell_rate
        CartItem.objects.create(
            cart=cart,
            currency=currency,
            amount=amount,
            operation_type=operation_type,
            rate=rate
        )
        messages.success(request, 'Валюта добавлена в корзину')
        return redirect('cart')
    return render(request, 'add_to_cart.html', {'currency': currency})

@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user, is_active=True).first()
    items = cart.items.all() if cart else []
    total = sum(item.total for item in items)
    commission = total * 0.01
    total_to_pay = total + commission
    return render(request, 'cart.html', {
        'cart': cart,
        'items': items,
        'cart_items': items,
        'total': total,
        'commission': commission,
        'total_to_pay': total_to_pay,
    })

@login_required
def remove_from_cart(request, item_id):
    CartItem.objects.filter(id=item_id, cart__user=request.user).delete()
    messages.success(request, 'Позиция удалена из корзины')
    return redirect('cart')

@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user, is_active=True).first()
    if not cart:
        messages.error(request, 'Корзина пуста')
        return redirect('cart')
    items = cart.items.all()
    if request.method == 'POST':
        # Имитация успешной оплаты
        for item in items:
            Transaction.objects.create(
                user=request.user,
                currency=item.currency,
                amount=item.amount,
                operation_type=item.operation_type,
                rate=item.rate,
                total=item.total,
                status='completed'
            )
        # Деактивируем все корзины пользователя
        Cart.objects.filter(user=request.user, is_active=True).update(is_active=False)
        # Создаём новую активную корзину
        Cart.objects.create(user=request.user, is_active=True)
        messages.success(request, 'Оплата прошла успешно! Обмен валюты выполнен.')
        return redirect('account')
    # Показываем страницу оплаты
    total = sum(item.total for item in items)
    commission = total * 0.01
    total_to_pay = total + commission
    return render(request, 'payment.html', {
        'cart': cart,
        'items': items,
        'total': total,
        'commission': commission,
        'total_to_pay': total_to_pay,
    })

def currency_detail(request, currency_id):
    currency = get_object_or_404(Currency, id=currency_id)
    if request.method == 'POST' and request.user.is_authenticated:
        operation_type = request.POST.get('operation_type')
        amount = request.POST.get('amount')
        if operation_type in ['buy', 'sell'] and amount:
            return redirect(f'/cart/add/{currency.id}/?amount={amount}&operation_type={operation_type}')
    return render(request, 'currency_detail.html', {'currency': currency})

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('account')
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form})

def reviews(request):
    reviews = Review.objects.filter(is_published=True).order_by('-created_at')
    form = None
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.name = request.user.get_full_name() or request.user.username
                review.is_published = False  # Модерация
                review.save()
                messages.success(request, 'Спасибо за ваш отзыв! Он появится после модерации.')
                return redirect('reviews')
        else:
            form = ReviewForm()
    return render(request, 'reviews.html', {'reviews': reviews, 'form': form})

@login_required
@require_POST
def exchange_view(request):
    from_currency_id = request.POST.get('from_currency')
    to_currency_id = request.POST.get('to_currency')
    from_amount = request.POST.get('amount')
    if not from_currency_id or not to_currency_id or from_currency_id == to_currency_id:
        messages.error(request, 'Выберите разные валюты для обмена!')
        return redirect('catalog')
    try:
        from_amount = float(from_amount)
    except (TypeError, ValueError):
        messages.error(request, 'Некорректная сумма')
        return redirect('catalog')
    from_currency = Currency.objects.get(id=from_currency_id)
    to_currency = Currency.objects.get(id=to_currency_id)
    # Проверка баланса пользователя по валюте, которую он отдаёт
    user_transactions = Transaction.objects.filter(user=request.user, currency=from_currency, status='completed')
    balance = 0.0
    for t in user_transactions:
        if t.operation_type == 'buy':
            balance += float(t.amount)
        elif t.operation_type == 'sell':
            balance -= float(t.amount)
    if from_amount > balance:
        messages.error(request, f'Недостаточно {from_currency.code} для обмена. Ваш баланс: {balance:.2f}')
        return redirect('catalog')
    # Считаем сколько получит пользователь
    rate = float(from_currency.sell_rate) / float(to_currency.buy_rate)
    to_amount = from_amount * rate
    # Создаём две транзакции
    Transaction.objects.create(
        user=request.user,
        currency=from_currency,
        amount=from_amount,
        operation_type='sell',
        rate=from_currency.sell_rate,
        total=from_amount * float(from_currency.sell_rate),
        status='completed'
    )
    Transaction.objects.create(
        user=request.user,
        currency=to_currency,
        amount=to_amount,
        operation_type='buy',
        rate=to_currency.buy_rate,
        total=to_amount * float(to_currency.buy_rate),
        status='completed'
    )
    messages.success(request, f'Обмен успешно выполнен: {from_amount} {from_currency.code} → {to_amount:.2f} {to_currency.code}')
    return redirect('account')
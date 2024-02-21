from datetime import datetime, date
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView

from ChicPhoto import settings
from chic_photo.forms import OrderForm, UserForm, PhotographerForm, PortfolioForm
from chic_photo.models import User, StudioSpace, Photographer, Order, PhotoDirectory


# Create your views here.

def user_form_view(request):
    user_instance = User.objects.get(pk=request.user.pk)  # Получаем текущего пользователя

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user_instance)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Замените 'success_url' на URL страницы после успешной отправки формы
    else:
        form = UserForm(instance=user_instance)
    return render(request, 'includes/profile_form.html', {'form': form})


def photographer_form_view(request):
    photographer_instance = Photographer.objects.get(user=request.user)

    if request.method == 'POST':
        form = PhotographerForm(request.POST, instance=photographer_instance)
        portfolio_form = PortfolioForm(request.POST, request.FILES)
        if form.is_valid() and portfolio_form.is_valid():
            form.save()
            portfolio = portfolio_form.save(commit=False)
            portfolio.photographer = photographer_instance
            portfolio.save()
            return redirect('profile')  # Перенаправляем на профиль при успешной отправке формы
        else:
            print(form.errors)  # Выводим ошибки формы PhotographerForm
            print(portfolio_form.errors)  # Выводим ошибки формы PortfolioForm
    else:
        form = PhotographerForm(instance=photographer_instance)
        portfolio_form = PortfolioForm()

    return render(request, 'includes/photographer.html', {'form': form, 'portfolio_form': portfolio_form})

def index(request):
    return render(request, 'index.html')

class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return JsonResponse({'message': 'Неверные учетные данные'}, status=401)

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/reg.html')
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Пользователь с таким email уже существует'}, status=400)
        user = User.objects.create_user(email=email, password=password)
        login(request, user)
        return redirect('index')

class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return redirect('index')

@login_required
def profile(request):
    user = request.user
    role = user.get_role()
    return render(request, 'profile.html', {'user': user, 'role': role,})


def order_form(request):
    pass


def profile_form(request):
    return None
def studiospaces(request):
    return None
class StudioSpaceList(ListView):
    model = StudioSpace
    template_name = 'spaces.html'
    context_object_name = 'list_studios'
    extra_context = {'title': 'Студии'}

@login_required
def get_order_form(request):
    if request.method == 'GET':
        # Создаем форму OrderForm
        form = OrderForm()
        # Возвращаем HTML-код формы в формате JSON
        form_html = render(request, 'includes/order_form.html', {'form': form})
        return form_html
    elif request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():

            order = form.save(commit=False)
            order.userID = request.user
            scheduled_date = datetime.strptime(request.POST['scheduledDate'], '%Y-%m-%d').date()
            time_from = datetime.strptime(request.POST['timeFrom'], '%H:%M').time()
            time_to = datetime.strptime(request.POST['timeTo'], '%H:%M').time()

            order_time_from = datetime.combine(scheduled_date, time_from)
            order_time_to = datetime.combine(scheduled_date, time_to)

            time_difference = (order_time_to - order_time_from).total_seconds() / 3600
            time_difference_decimal = Decimal(str(time_difference))

            total_cost = time_difference_decimal * (
                        Decimal(order.serviceID.cost) + Decimal(order.spaceID.costPerHour))
            order.totalCost = total_cost

            # Устанавливаем идентификатор аутентифицированного пользователя как userId


            order.save()
            return redirect('index')
        else:
            errors = dict([(field, [error for error in errors]) for field, errors in form.errors.items()])
            return JsonResponse({'success': False, 'errors': errors})
class Photographers(ListView):
    model = Photographer
    template_name = 'photographers.html'
    context_object_name = 'photographers'


def order_status(request):
    return None
def generate_invoice(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return HttpResponse("Order not found.")

    # Создание текстового файла для чека
    invoice_content = f"Чек для заказа #{order_id}\n\n"
    invoice_content += f"Пользователь: {order.userID.first_name} {order.userID.last_name}\n"
    invoice_content += f"Услуга: {order.serviceID.serviceName}\n"
    invoice_content += f"Фотограф: {order.photographerID.user.first_name} {order.photographerID.user.last_name}\n"
    invoice_content += f"Место: {order.spaceID.spaceName}\n"
    invoice_content += f"Дата: {order.scheduledDate}\n"
    invoice_content += f"Время с: {order.timeFrom} до {order.timeTo}\n"
    invoice_content += f"Общая стоимость: {order.totalCost}\n"

    # Путь к файлу
    file_path = f"{settings.BASE_DIR}/chic_photo/invoices/{order_id}.txt"

    # Запись содержимого чека в файл
    with open(file_path, 'w', encoding='utf-8') as invoice_file:
        invoice_file.write(invoice_content)

    return HttpResponse("Invoice generated successfully.")
def orders(request):
    if request.user.RoleID.id == 2:
        all_orders = Order.objects.filter(userID=request.user.id, active=True)
        today_orders = all_orders.filter(scheduledDate=date.today(), userID=request.user.id, active=True)

    elif request.user.RoleID.id == 3:
        all_orders = Order.objects.all()
        today_orders = Order.objects.filter(scheduledDate=date.today())

    elif request.user.RoleID.id == 1:
        all_orders = Order.objects.filter(userID=request.user.id, active=True)
        today_orders = Order.objects.filter(scheduledDate=date.today(), userID=request.user.id, active=True)

    return render(request, 'orders.html', {'all_orders': all_orders, 'today_orders': today_orders})


@login_required
def cancel_order(request, order_id):
    if request.method == 'POST':
        order = Order.objects.get(id=order_id)
        order.active = False
        order.save()
    return redirect('orders')  # Предполагая, что у вас есть имя URL для всех заказов
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView
from django.forms import inlineformset_factory
from .models import Receipt, ReceiptProduct, Product
from .forms import ReceiptForm, ReceiptProductForm
from .models import *
from .forms import *
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.exceptions import PermissionDenied

ReceiptProductFormSet = inlineformset_factory(
    Receipt,
    ReceiptProduct,
    form=ReceiptProductForm,
    extra=1,
    can_delete=True
)


def is_manager_or_admin(user):
    return user.role in ['manager', 'admin']


def manager_or_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role not in ['manager', 'admin']:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
def store_list(request):
    stores = Store.objects.all()
    # Проверяем, может ли пользователь редактировать (только менеджеры и админы)
    can_edit = request.user.role in ['manager', 'admin']

    return render(request, 'receipts/store_list.html', {
        'stores': stores,
        'can_edit': can_edit,
        'is_cashier': request.user.role == 'cashier'
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('receipt_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def is_manager(user):
    return user.role == 'manager'


def is_cashier(user):
    return user.role == 'cashier'


@login_required
def receipt_list(request):
    if request.user.role == 'cashier':
        receipts = Receipt.objects.filter(cashier=request.user)
    else:
        receipts = Receipt.objects.all()

    return render(request, 'receipts/receipt_list.html', {
        'receipts': receipts,
        'can_create': request.user.role in ['cashier', 'manager', 'admin']
    })


# Добавим аналогичные представления для всех сущностей
@login_required
def store_list(request):
    stores = Store.objects.all()
    return render(request, 'receipts/store_list.html', {'stores': stores})


@login_required
def receipt_detail(request, pk):
    receipt = get_object_or_404(Receipt, pk=pk)
    # Кассир может видеть только свои чеки
    if request.user.role == 'cashier' and receipt.cashier != request.user:
        return redirect('receipt_list')
    return render(request, 'receipts/receipt_detail.html', {'receipt': receipt})


@login_required
def receipt_create(request):
    products = Product.objects.all()  # Получаем все товары для выпадающего списка

    if request.method == 'POST':
        form = ReceiptForm(request.POST)
        if form.is_valid():
            receipt = form.save()
            return redirect('receipt_list')
    else:
        form = ReceiptForm()

    return render(request, 'receipts/receipt_form.html', {
        'form': form,
        'formset': form.product_formset,
        'products': products  # Добавляем товары в контекст
    })


@login_required
@manager_or_admin_required
def store_create(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store_list')
    else:
        form = StoreForm()
    return render(request, 'receipts/store_form.html', {'form': form})


@login_required
def receipt_update(request, pk):
    receipt = get_object_or_404(Receipt, pk=pk)
    # Проверка прав доступа
    if request.user.role == 'cashier' and receipt.cashier != request.user:
        return redirect('receipt_list')

    if request.method == 'POST':
        form = ReceiptForm(request.POST, instance=receipt, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('receipt_detail', pk=receipt.pk)
    else:
        form = ReceiptForm(instance=receipt, user=request.user)

    return render(request, 'receipts/receipt_form.html', {
        'form': form,
        'formset': form.product_formset,
        'products': Product.objects.all()
    })


@login_required
def receipt_delete(request, pk):
    receipt = get_object_or_404(Receipt, pk=pk)
    # Проверка прав доступа
    if request.user.role == 'cashier':
        return redirect('receipt_list')

    if request.method == 'POST':
        receipt.delete()
        return redirect('receipt_list')
    return render(request, 'receipts/receipt_confirm_delete.html', {'receipt': receipt})


# Представления для магазинов (только для менеджеров)
@login_required
def store_list(request):
    stores = Store.objects.all()
    return render(request, 'receipts/store_list.html', {'stores': stores})


@login_required
def store_detail(request, pk):
    store = get_object_or_404(Store, pk=pk)
    return render(request, 'receipts/store_detail.html', {'store': store})


@login_required
@manager_or_admin_required
def store_update(request, pk):
    store = get_object_or_404(Store, pk=pk)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect('store_list')
    else:
        form = StoreForm(instance=store)
    return render(request, 'receipts/store_form.html', {'form': form})


@login_required
@manager_or_admin_required
def store_delete(request, pk):
    store = get_object_or_404(Store, pk=pk)
    if request.method == 'POST':
        store.delete()
        return redirect('store_list')
    return render(request, 'receipts/store_confirm_delete.html', {'store': store})


class ReceiptCreateView(CreateView):
    model = Receipt
    form_class = ReceiptForm
    template_name = 'receipts/receipt_form.html'
    success_url = '/receipts/'


class ReceiptUpdateView(UpdateView):
    model = Receipt
    form_class = ReceiptForm
    template_name = 'receipts/receipt_form.html'
    success_url = reverse_lazy('receipt_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ReceiptProductFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = ReceiptProductFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


# Представления для клиентов (только для менеджеров)
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'receipts/customer_list.html', {'customers': customers})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'receipts/customer_detail.html', {'customer': customer})


@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'receipts/customer_form.html', {'form': form})


@login_required
@manager_or_admin_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'receipts/customer_form.html', {'form': form})


@login_required
@manager_or_admin_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    return render(request, 'receipts/customer_confirm_delete.html', {'customer': customer})


# Представления для категорий товаров (только для менеджеров)
@login_required
def category_list(request):
    categories = ProductCategory.objects.all()
    return render(request, 'receipts/category_list.html', {'categories': categories})


@login_required
def category_detail(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    return render(request, 'receipts/category_detail.html', {'category': category})


@login_required
@manager_or_admin_required
def category_create(request):
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = ProductCategoryForm()
    return render(request, 'receipts/category_form.html', {'form': form})


@login_required
@manager_or_admin_required
def category_update(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_detail', pk=category.pk)
    else:
        form = ProductCategoryForm(instance=category)
    return render(request, 'receipts/category_form.html', {'form': form})


@login_required
@manager_or_admin_required
def category_delete(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'receipts/category_confirm_delete.html', {'category': category})


# Представления для товаров (только для менеджеров)
@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'receipts/product_list.html', {'products': products})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'receipts/product_detail.html', {'product': product})


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'receipts/product_form.html', {'form': form})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'receipts/product_form.html', {'form': form})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'receipts/product_confirm_delete.html', {'product': product})


@login_required
def employee_list(request):
    if request.user.role != 'admin':
        raise PermissionDenied

    employees = CustomUser.objects.all().order_by('role', 'username')
    return render(request, 'receipts/employee_list.html', {
        'employees': employees
    })

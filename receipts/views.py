from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView
from django.forms import inlineformset_factory
from .models import Receipt, ReceiptProduct, Product
from .forms import ReceiptForm, ReceiptProductForm
from .models import Receipt
from .forms import ReceiptForm, ReceiptProductFormSet
from django.urls import reverse_lazy

ReceiptProductFormSet = inlineformset_factory(
    Receipt,
    ReceiptProduct,
    form=ReceiptProductForm,
    extra=1,
    can_delete=True
)


def receipt_list(request):
    receipts = Receipt.objects.all()
    return render(request, 'receipts/receipt_list.html', {'receipts': receipts})


def receipt_detail(request, pk):
    receipt = get_object_or_404(Receipt, pk=pk)
    return render(request, 'receipts/receipt_detail.html', {'receipt': receipt})


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

def receipt_update(request, pk):
    receipt = get_object_or_404(Receipt, pk=pk)
    if request.method == 'POST':
        form = ReceiptForm(request.POST, instance=receipt)
        if form.is_valid():
            form.save()
            return redirect('receipt_detail', pk=receipt.pk)
    else:
        form = ReceiptForm(instance=receipt)

    return render(request, 'receipts/receipt_form.html', {
        'form': form,
        'formset': form.product_formset
    })


def receipt_delete(request, pk):
    receipt = get_object_or_404(Receipt, pk=pk)
    if request.method == 'POST':
        receipt.delete()
        return redirect('receipt_list')
    return render(request, 'receipts/receipt_confirm_delete.html', {'receipt': receipt})


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
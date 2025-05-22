from django import forms
from .models import Receipt, ReceiptProduct, Product


class ReceiptProductForm(forms.ModelForm):
    # Добавляем поле для поиска товаров
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'product-select'}))

    quantity = forms.IntegerField(min_value=1, initial=1)

    class Meta:
        model = ReceiptProduct
        fields = ['product', 'quantity']


# Увеличиваем количество дополнительных форм
ReceiptProductFormSet = forms.inlineformset_factory(
    Receipt,
    ReceiptProduct,
    form=ReceiptProductForm,
    extra=1,  # Можно добавить сразу несколько пустых строк
    can_delete=True
)


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['number', 'date_time', 'store', 'customer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_formset = ReceiptProductFormSet(
            instance=self.instance,
            data=self.data if self.is_bound else None,
            files=self.files if self.is_bound else None,
            prefix='products'
        )

    def is_valid(self):
        return super().is_valid() and self.product_formset.is_valid()

    def save(self, commit=True):
        # Сначала сохраняем чек
        receipt = super().save(commit=commit)

        if commit:
            # Сохраняем товары
            self.product_formset.instance = receipt
            self.product_formset.save()

            # Принудительно пересчитываем сумму
            receipt._calculate_total()
            receipt.save()

        return receipt

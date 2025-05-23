from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class CustomUser(AbstractUser):
    ROLES = (
        ('cashier', 'Кассир'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='cashier')

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        # Добавьте это:
        db_table = 'custom_user'

    def __str__(self):
        return self.username

    def get_role_display(self):
        return dict(self.ROLES).get(self.role, self.role)


class Store(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Receipt(models.Model):
    number = models.CharField(max_length=50)
    date_time = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Добавлено default=0
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cashier = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='ReceiptProduct')

    def save(self, *args, **kwargs):
        # Сначала сохраняем чек (чтобы получить ID)
        super().save(*args, **kwargs)

        # Если чек уже существует, пересчитываем сумму
        if self.pk:
            self._calculate_total()
            # Сохраняем снова с обновленной суммой
            super().save(*args, **kwargs)

    def _calculate_total(self):
        """Вычисляет общую сумму на основе связанных товаров"""
        total = sum(
            item.product.price * item.quantity
            for item in self.receiptproduct_set.all()
        )
        self.total_amount = total

    def __str__(self):
        return f"Чек №{self.number} от {self.date_time}"


class ReceiptProduct(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Количество товара

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

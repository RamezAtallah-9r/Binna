from django.db import models
from binnacustomer.models import Customer


# =========================
# City Model
# =========================
class CityManager(models.Manager):
    def create_city(self, name):
        return self.create(name=name)

    def get_all_cities(self):
        return self.all()

    def get_city_by_id(self, city_id):
        return self.get(id=city_id)


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    objects = CityManager()

    def __str__(self):
        return self.name


# =========================
# Supplier Category Model
# =========================
class SupplierCategoryManager(models.Manager):
    def create_category(self, name):
        return self.create(name=name)

    def get_all_categories(self):
        return self.all()

    def get_category_by_id(self, category_id):
        return self.get(id=category_id)


class SupplierCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    objects = SupplierCategoryManager()

    def __str__(self):
        return self.name


# =========================
# Inventory Category Model
# =========================
class InventoryCategoryManager(models.Manager):
    def create_category(self, name):
        return self.create(name=name)

    def get_all_categories(self):
        return self.all()

    def get_category_by_id(self, category_id):
        return self.get(id=category_id)


class InventoryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    objects = InventoryCategoryManager()

    def __str__(self):
        return self.name


# =========================
# Supplier Model
# =========================
class SupplierManager(models.Manager):

    def create_supplier(self, post_data, image=None):
        return self.create(
            store_name=post_data['store_name'],
            owner_name=post_data['owner_name'],
            phone=post_data['phone'],
            email=post_data['email'],
            city=City.objects.get(id=post_data['city_id']),
            street=post_data['street'],
            description=post_data.get('description', ''),
            category=SupplierCategory.objects.get(id=post_data['category_id']),
            image=image
        )

    def get_all_suppliers(self):
        return self.all()

    def get_supplier_by_id(self, supplier_id):
        return self.get(id=supplier_id)

    def update_supplier(self, supplier_id, post_data, image=None):
        supplier = self.get(id=supplier_id)

        supplier.store_name = post_data.get(
            'store_name',
            supplier.store_name
        )

        supplier.owner_name = post_data.get(
            'owner_name',
            supplier.owner_name
        )

        supplier.phone = post_data.get(
            'phone',
            supplier.phone
        )

        supplier.email = post_data.get(
            'email',
            supplier.email
        )

        supplier.street = post_data.get(
            'street',
            supplier.street
        )

        supplier.description = post_data.get(
            'description',
            supplier.description
        )

        if post_data.get('city_id'):
            supplier.city = City.objects.get(
                id=post_data['city_id']
            )

        if post_data.get('category_id'):
            supplier.category = SupplierCategory.objects.get(
                id=post_data['category_id']
            )

        if image:
            supplier.image = image

        supplier.save()

        return supplier

    def delete_supplier(self, supplier_id):
        supplier = self.get(id=supplier_id)
        supplier.delete()


class Supplier(models.Model):
    store_name = models.CharField(max_length=255)

    owner_name = models.CharField(max_length=255)

    phone = models.CharField(max_length=20)

    email = models.EmailField()

    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name='suppliers'
    )

    street = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    category = models.ForeignKey(
        SupplierCategory,
        on_delete=models.PROTECT,
        related_name='suppliers'
    )

    image = models.ImageField(
        upload_to='img/suppliers/',
        default='img/suppliers/default.png',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    objects = SupplierManager()

    def __str__(self):
        return self.store_name


# =========================
# Inventory Model
# =========================
class InventoryManager(models.Manager):

    def create_inventory(self, post_data, image=None):
        return self.create(
            supplier=Supplier.objects.get(
                id=post_data['supplier_id']
            ),

            name=post_data['name'],

            category=InventoryCategory.objects.get(
                id=post_data['category_id']
            ),

            amount=post_data['amount'],

            buy_price=post_data['buy_price'],

            sell_price=post_data['sell_price'],

            image=image
        )

    def get_all_inventory(self):
        return self.all()

    def get_inventory_by_id(self, inventory_id):
        return self.get(id=inventory_id)

    def get_supplier_inventory(self, supplier_id):
        return self.filter(
            supplier_id=supplier_id
        )

    def update_inventory(
        self,
        inventory_id,
        post_data,
        image=None
    ):
        inventory = self.get(id=inventory_id)

        inventory.name = post_data.get(
            'name',
            inventory.name
        )

        inventory.amount = post_data.get(
            'amount',
            inventory.amount
        )

        inventory.buy_price = post_data.get(
            'buy_price',
            inventory.buy_price
        )

        inventory.sell_price = post_data.get(
            'sell_price',
            inventory.sell_price
        )

        if post_data.get('category_id'):
            inventory.category = InventoryCategory.objects.get(
                id=post_data['category_id']
            )

        if image:
            inventory.image = image

        inventory.save()

        return inventory

    def delete_inventory(self, inventory_id):
        inventory = self.get(id=inventory_id)
        inventory.delete()


class Inventory(models.Model):

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='inventory'
    )

    name = models.CharField(max_length=255)

    category = models.ForeignKey(
        InventoryCategory,
        on_delete=models.PROTECT,
        related_name='inventory'
    )

    amount = models.PositiveIntegerField(
        default=0
    )

    buy_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    sell_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to='img/inventory/',
        default='img/inventory/default.png',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    objects = InventoryManager()

    def __str__(self):
        return self.name


# =========================
# Order Model
# =========================
class OrderManager(models.Manager):

    def create_order(
        self,
        customer,
        supplier,
        total_amount
    ):
        return self.create(
            customer=customer,
            supplier=supplier,
            total_amount=total_amount
        )

    def get_all_orders(self):
        return self.all()

    def get_order_by_id(self, order_id):
        return self.get(id=order_id)

    def get_customer_orders(self, customer_id):
        return self.filter(
            customer_id=customer_id
        )

    def get_supplier_orders(self, supplier_id):
        return self.filter(
            supplier_id=supplier_id
        )

    def update_status(
        self,
        order_id,
        status
    ):
        order = self.get(id=order_id)

        order.status = status

        order.save()

        return order

    def delete_order(self, order_id):
        order = self.get(id=order_id)
        order.delete()


class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('preparing', 'Preparing'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='provider_orders'
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    objects = OrderManager()

    def __str__(self):
        return f"Order #{self.id}"


# =========================
# Order Item Model
# =========================
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='order_items'
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return (
            f"{self.inventory.name}"
            f" - Order #{self.order.id}"
        )
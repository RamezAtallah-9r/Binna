import bcrypt
import re
from django.db import models

# ── Blueprint Model ────────────────────────────────────────────────────────
class Blueprint(models.Model):
    image = models.ImageField(upload_to='blueprints/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    analysis_result = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Blueprint uploaded on {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"

# ── Customer Manager ───────────────────────────────────────────────────────
class CustomerManager(models.Manager):
    def registration_validator(self, post_data):
        errors = {}
        # 1. الأسماء
        if len(post_data.get('first_name', '')) < 2:
            errors['first_name'] = 'First name must be at least 2 characters.'
        if len(post_data.get('last_name', '')) < 2:
            errors['last_name'] = 'Last name must be at least 2 characters.'

        # 2. البريد الإلكتروني
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, post_data.get('email', '')):
            errors['email'] = 'Please enter a valid email address.'
        elif Customer.objects.filter(email=post_data.get('email')).exists():
            errors['email_taken'] = 'An account with this email already exists.'

        # 3. الهاتف
        phone_regex = r'^\+?(\d{10,15})$'
        if not re.match(phone_regex, post_data.get('phone', '')):
            errors['phone'] = 'Please enter a valid phone number (10-15 digits).'

        # 4. كلمة المرور
        password = post_data.get('password', '')
        password_regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
        if len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters.'
        elif not re.match(password_regex, password):
            errors['password'] = 'Password must include letters, numbers, and special characters.'

        return errors

    def create_customer(self, post_data):
        # تشفير كلمة المرور باستخدام bcrypt
        hashed_pw = bcrypt.hashpw(post_data['password'].encode(), bcrypt.gensalt()).decode('utf-8')
        
        return self.create(
            first_name=post_data['first_name'],
            last_name=post_data['last_name'],
            city=post_data['city'],
            email=post_data['email'],
            phone=post_data['phone'],
            password=hashed_pw,
            active=True
        )

# ── Customer Model ─────────────────────────────────────────────────────────
class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomerManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # دوال المساعدة (Utility Methods)
    def update_customer_info(self, post_data):
        self.first_name = post_data.get('first_name', self.first_name)
        self.last_name = post_data.get('last_name', self.last_name)
        self.city = post_data.get('city', self.city)
        self.phone = post_data.get('phone', self.phone)
        self.save()
        return self

def delete_customer(self, customer_id):
    customer = Customer.objects.get(id=customer_id)
    customer.delete()

def get_all_customers(self):
    return Customer.objects.all()

def get_customer_by_id(self, customer_id):
    return Customer.objects.get(id=customer_id)

def get_customer_by_email(self, email):
    return Customer.objects.filter(email=email)

def activate_customer(self, customer_id):
    customer = Customer.objects.get(id=customer_id)
    customer.active = True
    customer.save()
    return customer

def deactivate_customer(self, customer_id):
    customer = Customer.objects.get(id=customer_id)
    customer.active = False
    customer.save()
    return customer



from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid, random
from PIL import Image
from django.utils.deconstruct import deconstructible
from django.core.validators import RegexValidator
from django.utils import timezone
import os
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from .utils import encode_uuid_to_base64

# Helper function to rename files to avoid collision\
PAYMENT_METHOD_CHOICES = [
    ('Cash', 'Cash'),
    ('Credit Card', 'Credit Card'),
    ('Debit Card', 'Debit Card'),
    ('Online Payment', 'Online Payment'),
]

@deconstructible
class UploadToPathAndRename:
    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = f'{uuid.uuid4().hex}.{ext}'
        return os.path.join(self.sub_path, filename)
    

def optimize_image(image_field, path, filename):
    img = Image.open(image_field)
    max_size = (800, 800)
    img.thumbnail(max_size, Image.LANCZOS)
    if img.format.lower() not in ['jpeg', 'jpg']:
        img = img.convert('RGB')
    img_path = os.path.join(path, filename)
    full_img_path = os.path.join(settings.MEDIA_ROOT, img_path)    
    os.makedirs(os.path.dirname(full_img_path), exist_ok=True)
    img.save(full_img_path, optimize=True, quality=85)
    return img_path

class BaseModel(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True  # This model won't create a table, just be inherited by other models

# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        user.set_password(password)  # Securely hash password
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user_code = models.CharField(max_length=7, unique=True, editable=False)
    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    user_phone_number = models.CharField(max_length=15, unique=True, validators=[
        RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Phone number must be entered in the format: "999999999". Up to 15 digits allowed.')
    ])    
    role = models.CharField(max_length=10, choices=[('owner', 'Owner')], default='owner')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to=UploadToPathAndRename('user_images/'), blank=True, null=True, default='default.jpg')

    objects = UserManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['username', 'name']

    def save(self, *args, **kwargs):
        if not self.user_code:
            self.user_code = self.generate_custom_code()

        if self.profile_image and not self.profile_image.name == 'default.jpg':
            image_filename = f'{self.user_code}_{self.username}.jpg'
            self.profile_image = optimize_image(self.profile_image, 'user_images', image_filename)

        super().save(*args, **kwargs)

    def generate_custom_code(self):
        return str(random.randint(1000000, 9999999))

    def __str__(self):
        self.encoded_user_id = encode_uuid_to_base64(self.user_id)
        return self.encoded_user_id

# Shop Model
class Shop(models.Model):
    shop_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    shop_code = models.CharField(max_length=7, unique=True, editable=False)
    shop_name = models.CharField(max_length=255)
    shop_email = models.EmailField(unique=True)
    shop_address = models.CharField(max_length=255)
    shop_phone_number = models.CharField(max_length=15, unique=True, validators=[
        RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Phone number must be entered in the format: "999999999". Up to 15 digits allowed.')
    ])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops')
    shop_image = models.ImageField(upload_to=UploadToPathAndRename('shop_images/'), blank=True, null=True, default='default.jpg')

    def save(self, *args, **kwargs):
        if not self.shop_code:
            self.shop_code = self.generate_custom_code()

        if self.shop_image and not self.shop_image.name == 'default.jpg':
            image_filename = f'{self.shop_code}_{self.shop_name}.jpg'
            self.shop_image = optimize_image(self.shop_image, 'shop_images', image_filename)

        super().save(*args, **kwargs)

    def generate_custom_code(self):
        return str(random.randint(1000000, 9999999))

    def __str__(self):
         return self.shop_name  # Convert UUID to string

class Employee(BaseModel):
    employee_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    employee_code = models.CharField(max_length=8, unique=True, validators=[
        RegexValidator(regex=r'^[A-Za-z]{3}\d{5}$', message='Employee ID must start with 3 letters followed by 5 digits.')
    ])
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, validators=[
        RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Phone number must be entered in the format: "999999999". Up to 15 digits allowed.')
    ])
    address = models.TextField()
    role = models.CharField(max_length=50)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    employee_image = models.ImageField(upload_to=UploadToPathAndRename('employee_images/'), blank=True, null=True, default='default.jpg')

    def save(self, *args, **kwargs):
        if not self.employee_code:
            self.employee_code = self.generate_employee_id()

        if not self.pk or 'password' in self.__dict__:  # Ensure password is hashed when creating a new instance
            self.password = make_password(self.password)

        if self.employee_image and not self.employee_image.name == 'default.jpg':
            image_filename = f'{self.employee_code}_{self.name}.jpg'
            self.employee_image = optimize_image(self.employee_image, 'employee_images', image_filename)

        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def generate_employee_id(self):
        return f"{uuid.uuid4().hex[:3].upper()}{random.randint(10000, 99999)}"

    def __str__(self):
        return f"{self.name} - {self.role}"
    
class Shift(BaseModel):
    shift_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    shift_name = models.CharField(max_length=255,unique=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    employees = models.ManyToManyField(Employee)
    date = models.DateField(default=timezone.now)  # Daily stock entry
    
    def __str__(self):
        # Extracting the date part from the start_time field
        return f"{self.shift_name} on {self.start_time.date()}"
    
class Product(BaseModel):
    product_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    product_code = models.CharField(max_length=7, unique=True, editable=False)
    name = models.CharField(max_length=255)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)  # e.g., price for 1 liter
    unit = models.CharField(
        max_length=10,
        choices=[
            ('l', 'Liters'),
            ('g', 'Grams'),
            ('kg', 'Kilograms'),
            ('units', 'Units'),
        ],
        default='l'
    )  
    product_image = models.ImageField(upload_to='product_images/', blank=True, null=True, default='default.jpg')

    def save(self, *args, **kwargs):
        # Generate a product code if it doesn't exist
        if not self.product_code:
            self.product_code = self.generate_custom_code()
        super().save(*args, **kwargs)

    def generate_custom_code(self):
        return str(uuid.uuid4().hex[:7]).upper()

    def __str__(self):
        return f"{self.name} ({self.product_code})"


class Stock(BaseModel):
    stock_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    date = models.DateField(default=timezone.now)  # Daily stock entry
    opening_stock = models.PositiveIntegerField(default=0)  # Stock at the start of the day
    added_stock = models.PositiveIntegerField(default=0)  # New stock added during the day
    sold_quantity = models.PositiveIntegerField(default=0)  # Quantity sold during the day
    closing_stock = models.PositiveIntegerField(editable=False)  # Auto-calculated based on sales and additions

    def save(self, *args, **kwargs):
        # Calculate closing stock
        self.closing_stock = self.opening_stock + self.added_stock - self.sold_quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.date}"


class ExpenseType(BaseModel):
    expense_type_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ('name', 'user', 'shop')

    def __str__(self):
        return self.name
    
# Expense Model
class Expense(BaseModel):
    expense_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    type = models.ForeignKey(ExpenseType, on_delete=models.CASCADE)  
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='cash')  # Payment method

    def __str__(self):
        return f"{self.type} - {self.amount}"

# Sale Model
class Sale(BaseModel):
    sale_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    date = models.DateField()
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='cash')  # Payment method

    def __str__(self):
        return f"Sale of {self.product.name} - {self.quantity}"

class Profit(BaseModel):
    profit_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    total_income = models.DecimalField(max_digits=10, decimal_places=2)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2)
    cost_of_goods_sold = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    operating_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Calculated fields
    gross_profit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    net_profit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shortage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    loss = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Added Loss field

    date = models.DateField()
   
    def save(self, *args, **kwargs):
        # Calculate Gross Profit
        self.gross_profit = self.total_income - self.cost_of_goods_sold
        
        # Calculate Net Profit
        self.net_profit = self.gross_profit - self.operating_expenses - self.total_expenses
        
        # Calculate Shortage
        if self.total_expenses > self.total_income:
            self.shortage = self.total_expenses - self.total_income
        else:
            self.shortage = 0
        
        # Calculate Loss
        if self.net_profit < 0:  # If there's a loss, it's the absolute value of net profit
            self.loss = abs(self.net_profit)
        else:
            self.loss = 0  # Set loss to 0 if no loss occurs

        super().save(*args, **kwargs)

    def __str__(self):
        return (f"Profit for {self.date} - "
                f"Gross: {self.gross_profit}, "
                f"Net: {self.net_profit}, "
                f"Shortage: {self.shortage}, "
                f"Loss: {self.loss}")


# class Log(models.Model):
#     ACTION_CHOICES = [
#         ('CREATE', 'Create'),
#         ('UPDATE', 'Update'),
#         ('DELETE', 'Delete'),
#     ]

#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
#     shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
#     action = models.CharField(max_length=10, choices=ACTION_CHOICES)
#     model_name = models.CharField(max_length=100)
#     instance_id = models.UUIDField()  # Use UUID to match the primary keys of User and Shop
#     description = models.TextField()
#     timestamp = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"{self.user} {self.action} on {self.model_name} (ID: {self.instance_id})"    
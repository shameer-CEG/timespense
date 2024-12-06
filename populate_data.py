import os
import django
import random
from faker import Faker
import sys
from datetime import datetime, timedelta

# Ensure the current script can find the Django project
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timespense.settings')  # Ensure this is correct

django.setup()
from timesaver.models import *  # Import your models
from django.core.files import File  # For image file handling

# Create a Faker instance
fake = Faker()
from datetime import datetime, timedelta
import random
from django.utils import timezone
from django.contrib.auth.hashers import make_password

PAYMENT_METHOD_CHOICES = [
    ('credit_card', 'Credit Card'),
    ('debit_card', 'Debit Card'),
    ('online', 'Online Payment'),
]
payment_methods = [method[0] for method in PAYMENT_METHOD_CHOICES]


# Generate a random date within a specified range
def random_date(start_year=2022, end_year=2023):
    start_date = datetime(year=start_year, month=1, day=4)
    end_date = datetime(year=end_year, month=12, day=20)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

# Generate a random date within a specified range
def random_date_shift(start_year=2024, end_year=2024):
    start_date = datetime(year=start_year, month=1, day=4)
    end_date = datetime(year=end_year, month=1, day=6)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

# Create user instances
def create_users(n):
    for _ in range(n):
        user = User.objects.create_user(
            email=fake.email(),
            username=fake.user_name(),
            password='password',  # Default password
            name=fake.name(),
            user_phone_number=fake.phone_number(),
        )
        print(f'Created user: {user.email}')

# Create shop instances
def create_shops(n):
    for _ in range(n):
        shop = Shop.objects.create(
            shop_name=fake.company(),
            shop_email=fake.email(),
            shop_address=fake.address(),
            shop_phone_number=fake.phone_number(),
            user=random.choice(User.objects.all())
        )
        print(f'Created shop: {shop.shop_name}')

# Create employee instances for a specific shop
def create_employees(n, shop_email):
    user = random.choice(User.objects.all())
    shop = Shop.objects.filter(user=user, shop_email=shop_email).first()
    if not shop:
        print(f"No shop found with email {shop_email} for user {user.username}")
        return

    for _ in range(n):
        employee = Employee.objects.create(
            name=fake.name(),
            email=fake.email(),
            phone_number=fake.phone_number(),
            address=fake.address(),
            role=random.choice(['Manager', 'Cashier', 'Worker']),
            user=user,
            shop=shop
        )
        print(f'Created employee: {employee.name}')

# Create product instances for a specific shop
def create_products(n, shop_email):
    user = random.choice(User.objects.all())
    shop = Shop.objects.filter(user=user, shop_email=shop_email).first()
    
    if not shop:
        print(f"No shop found with email {shop_email} for user {user.username}")
        return

    for _ in range(n):
        product = Product.objects.create(
            name=fake.word(),
            price_per_unit=round(random.uniform(1.0, 100.0), 2),
            unit=random.choice(['l', 'g', 'kg', 'units']),
            user=user,
            shop=shop
        )
        print(f'Created product: {product.name}')

# Create stock entries for products in a specific shop
def create_stock_entries(n, shop_email):
    user = random.choice(User.objects.all())
    shop = Shop.objects.filter(user=user, shop_email=shop_email).first()
    if not shop:
        print("No shop found with the given email.")
        return

    products = Product.objects.filter(shop=shop)

    for _ in range(n):
        date = random_date()
        for product in products:
            opening_stock = random.randint(0, 100)
            added_stock = random.randint(0, 50)
            sold_quantity = random.randint(0, opening_stock + added_stock)
            closing_stock = max(opening_stock + added_stock - sold_quantity, 0)

            Stock.objects.create(
                product=product,
                date=date,
                opening_stock=opening_stock,
                added_stock=added_stock,
                sold_quantity=sold_quantity,
                closing_stock=closing_stock,
                user=user,
                shop=shop
            )
            print(f'Created stock entry for {product.name} on {date}')

# Create predefined expense types for a specific shop
def create_expense_types(shop_email):
    user = random.choice(User.objects.all())
    shop = Shop.objects.filter(user=user, shop_email=shop_email).first()
    expense_types = ['Rent', 'Utilities', 'Supplies', 'Salaries', 'Maintenance', 'Miscellaneous']
    
    for name in expense_types[:random.randint(4, 6)]:
        ExpenseType.objects.create(
            name=name,
            user=user,
            shop=shop
        )
        print(f'Created expense type: {name}')

# Create expense instances for a specific shop
def create_expenses(n, shop_email):
    user = random.choice(User.objects.all())
    shop = Shop.objects.filter(user=user, shop_email=shop_email).first()
    
    for _ in range(n):
        expense = Expense.objects.create(
            type=random.choice(ExpenseType.objects.filter(user=user, shop=shop)),
            amount=round(random.uniform(100.0, 1000.0), 2),
            description=fake.sentence(),
            date=random_date(),
            user=user,
            shop=shop,
            payment_method=random.choice(payment_methods)
        )
        print(f'Created expense: {expense.amount}')


# Create shift instances and assign employees for a specific shop
def create_shifts(n, shop_email):
    user = random.choice(User.objects.all())
    shop = Shop.objects.filter(user=user, shop_email=shop_email).first()
    employees = list(Employee.objects.filter(shop=shop))
    date = random_date_shift()
    for i in range(n):
        shift = Shift.objects.create(
            shift_name=f"{i}_shift",
            date=date,
            start_time=date,
            end_time=date,
            user=user,
            shop=shop
        )
        shift.employees.set(random.sample(employees, k=random.randint(1, len(employees))))
        shift.save()
        print(f'Created shift: {shift.shift_name}')

# Create sale instances for products in a specific shop
def create_sales(n, shop_email):
    user = random.choice(User.objects.all())
    shop = Shop.objects.filter(user=user, shop_email=shop_email).first()
    
    for _ in range(n):
        sale = Sale.objects.create(
            product=random.choice(Product.objects.filter(user=user, shop=shop)),
            quantity=random.randint(1, 5),
            total_amount=round(random.uniform(10.0, 500.0), 2),
            date=random_date(),
            shift=random.choice(Shift.objects.filter(shop=shop)),
            user=user,
            shop=shop,            
            payment_method=random.choice(payment_methods)

        )
        print(f'Created sale: {sale.total_amount}')


# Create profit instances for a specific shop
def create_profits(n, shop_email):
    user = random.choice(User.objects.all())
    shop = Shop.objects.filter(user=user, shop_email=shop_email).first()
    
    for _ in range(n):
        # Generate random values for total_income and total_expenses
        total_income = random.uniform(1000.0, 10000.0)
        total_expenses = random.uniform(500.0, 2000.0)

        # Calculate gross profit, net profit, shortage, and loss
        gross_profit = total_income - total_expenses if total_income >= total_expenses else 0.0
        net_profit = gross_profit  # Assuming no additional deductions for this example
        shortage = total_expenses - total_income if total_expenses > total_income else 0.0
        loss = shortage  # Set loss equal to shortage if expenses exceed income

        # Create a new Profit object
        profit = Profit.objects.create(
            total_income=total_income,
            total_expenses=total_expenses,
            date=random_date(),
            user=user,
            shop=shop,
            gross_profit=gross_profit,
            net_profit=net_profit,
            shortage=shortage,
            loss=loss
        )
        
        print(f'Created profit: {profit.gross_profit}, Shortage: {profit.shortage}, Loss: {profit.loss}')


if __name__ == '__main__':
    li = ['melissa56@example.net']
    # li = ['rachelorozco@example.com']
    # li = ['nrodriguez@example.com']
    create_users(1)       # Create users
    # create_shops(3)        # Create shops

    # for i in li:
    #     create_employees(6,i)    # Create employees
    #     create_products(15,i)     # Create products

    #     create_expense_types(i)   # Create 4 to 6 expense types
    #     create_profits(20,i)       # Create profit records
    #     create_shifts(3,i)       # Create shifts
    #     # create_shifts(3,i)       # Create shifts

    #     create_expenses(10,i)     # Create expenses
    #     create_expenses(5,i)     # Create expenses


    #     create_sales(5,i)        # Create sales
    #     create_sales(5,i)        # Create sales
    #     create_sales(6,i)        # Create sales
    #     create_sales(2,i)        # Create sales

    #     create_stock_entries(2,i)
        

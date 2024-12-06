from .forms import *
from django.core.mail import EmailMessage,send_mail
from django.core.mail.backends.console import EmailBackend
from django.shortcuts import render, redirect,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy,reverse
from django.contrib.auth.views import PasswordResetConfirmView,PasswordResetView
from django.contrib.auth import login,update_session_auth_hash,logout
from django.middleware.csrf import get_token
from .utils import encode_uuid_to_base64,decode_base64_to_uuid
from django.http import JsonResponse,Http404
from django.db.models import Sum,F
from django.utils.dateparse import parse_date
from datetime import date,timedelta
from django.utils.timezone import now
from django.utils.crypto import get_random_string

otp_storage = {}  # Temporary OTP storage (for production, use a database or cache)


# ^  Start Authentication

def signup_view(request):
    if request.method == 'POST':
        user_form = SignupForm(request.POST)
        shop_form = ShopForm(request.POST, request.FILES)

        if user_form.is_valid() and shop_form.is_valid():
            user = user_form.save(commit=False)
            user.email = user_form.cleaned_data.get('email')
            user.role = 'owner'
            user.save()

            shop = shop_form.save(commit=False)
            shop.user = user
            shop.save()

            messages.success(request, 'Registration successful!')
            return redirect('success')  # Change this to your success URL

        else:
            # Collect error messages from both forms
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

            for field, errors in shop_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

            # Redirect back to the signup form
            return redirect('signup')  # Ensure 'signup' matches your URL pattern

    else:
        user_form = SignupForm()
        shop_form = ShopForm()

    context = {
        'signup_form': user_form,
        'shop_form': shop_form,
    }
    return render(request, 'base.html', context)


# Login view
def login_view(request):
    print(request)
    form = LoginForm(request.POST or None)
    # print(form)
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data.get('user')
        # Ensure the user is an owner
        if user.role != 'owner':
            form.add_error(None, "You do not have permission to access the owner dashboard.")
        else:
            login(request, user)
            return redirect('overall_dashboard')

    return render(request, 'auth/owner/login.html', {'form': form})


# def employee_login_view(request):
#     form = LoginForm(request.POST or None)
#     if request.method == 'POST' and form.is_valid():
#         user = form.cleaned_data.get('user')

#         # Ensure the user is an employee (associated with an employee profile)
#         if not hasattr(user, 'employee'):
#             form.add_error(None, "You are not registered as an employee.")
#         else:
#             login(request, user)
#             return redirect('home')

#     return render(request, 'auth/employee/employee_login.html', {'form': form})

# Logout view
@login_required
def logout_view(request):
    logout(request)
    return redirect('/') 
# ^  end Authentication


# ^  Password Reset

# & Testing Forgot Password -BETA
def my_view(recipient,message):
    # Your view logic goes here

    # Assuming you have an email subject, message, and recipient
    subject = 'Test Email'
    print('hello')
    # Send the email using the console backend for debugging
      # Send the email using the console backend for debugging
    if settings.DEBUG:
        # Use the console backend for debugging
        backend = EmailBackend()
        email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [recipient])
        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient])
        backend.send_messages([email])
    else:
        email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [recipient])
        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient])
        email.send()

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')   # Your logic for forgot password goes here
        print(email)
        user = User.objects.filter(email=email)
        print(user.values_list('user_id')[0][0])
        message = f"http://127.0.0.1:8000/{user.values_list('user_id')[0][0]}/change-password/"
        print(message)
        my_view(email,message)
        # Send reset link or perform necessary actions
        messages.success(request, f'Password reset link sent to {email} successfully. ')
        return redirect('password')  # Redirect to the home page or any other page

    return render(request, 'auth/forgot_password.html')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'auth/forgot_password.html'
    email_template_name = 'auth/password_reset_email.html'
    subject_template_name = 'auth/password_reset_subject.txt'
    success_url = reverse_lazy('password')  # Redirect to the login page after a successful password reset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Set protocol and domain dynamically
        print(self.request.get_host(),)
        context.update({
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': '127.0.0.1:8000',  # Replace with your domain for production
        })
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Password reset email has been sent successfully. Please check your email.')
        return response

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    success_url = reverse_lazy('login')  # Redirect to the login page after a successful password reset
    form_class = CustomPasswordResetConfirmForm

    def form_valid(self, form):
        form.cleaned_data['formSubmitted'] = '1'
        response = super().form_valid(form)
        messages.success(self.request, 'Password has been reset successfully. You can now log in with your new password.')
        form.add_error('formSubmitted', '1')  # Set the flag indicating form submission
        return response
    
def change_password_view(request,shop_id=None):
    context = {}
    url = redirect('change_password')
    if shop_id:
       
        shop = get_object_or_404(Shop,  shop_id = decode_base64_to_uuid(shop_id), user=request.user)
        shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)
     
        context['shop'] = shop
        url = redirect('shop_change_password',shop_id)
        
        
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():

            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return url
        else:

            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)

    context['form'] = form 
    return render(request, 'auth/change_password.html', context)

# ^  Password Reset end

# ^ User start 

@login_required
def update_user(request,shop_id=None):
    context = {}
    url = redirect('update_user')
    user = get_object_or_404(User, user_code=request.user.user_code) 

    if shop_id:
       
        shop = get_object_or_404(Shop,  shop_id = decode_base64_to_uuid(shop_id), user=request.user)
        shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)
     
        context['shop'] = shop
        url = redirect('shop_update_user',shop_id)
        
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"User updated successfully.")
            return url 
    else:
        form = UserForm(instance=user)  

    context['form'] = form 
    return render(request, 'forms/user_form.html', context)

@login_required
def delete_user(request):
    user = get_object_or_404(User, user_code=request.user.user_code) 

    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # Generate and send OTP
        
        otp = get_random_string(length=6, allowed_chars="1234567890")
        otp_storage[user.email] = otp

        try:
            send_mail(
                subject="User Deletion OTP",
                message=f"Your OTP for deleting the user '{user.username}' is: {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
            )
            return JsonResponse({"status": "success", "message": f"OTP sent to {user.email}."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": "Failed to send OTP. Please try again."})

    elif request.method == "POST":
        # Handle OTP validation and shop deletion
        otp = request.POST.get("otp")
        if user.email in otp_storage and otp_storage[user.email] == otp:
            user.delete()
            del otp_storage[user.email]
            messages.success(request, f"User '{user.username}' deleted successfully.")
            return redirect('overall_shop_list')
        else:
            # return JsonResponse({"status": "error", "message": "Invalid to send OTP"})
            messages.error(request, f"Invalid OTP")
            return redirect('update_user')

    return redirect('update_user')

# ^ user end
 
# ^  Shop Start
@login_required
def create_shop(request):
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES)
        if form.is_valid():
            # Set the user to the currently logged-in user
            shop = form.save(commit=False)  # Create a shop instance without saving
            shop.user = request.user  # Set the user
            shop.save()  # Now save the shop
            return redirect('overall_shop_list')  # Redirect to your shop list or other relevant page
    else:
        form = ShopForm()

    return render(request, 'forms/shop/shop_form.html', {'form': form})
   

@login_required
def update_shop(request, shop_id):
    shop = get_object_or_404(Shop, shop_id=decode_base64_to_uuid(shop_id), user=request.user) 
    print(shop) # Ensure shop belongs to the user
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            form.save()
            messages.success(request, f"Shop updated successfully.")
            return redirect('update_shop', shop_id=shop_id)  # Redirect to the shop list page after update
    else:
        form = ShopForm(instance=shop)  # Pre-fill the form with existing data

    shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)
    return render(request, 'forms/shop/shop_form.html', {'form': form, 'shop': shop})

@login_required
def delete_shop(request, shop_id):
    shop = get_object_or_404(Shop, shop_id=decode_base64_to_uuid(shop_id), user=request.user) 
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # Generate and send OTP
        
        otp = get_random_string(length=6, allowed_chars="1234567890")
        otp_storage[shop.shop_email] = otp

        try:
            send_mail(
                subject="Shop Deletion OTP",
                message=f"Your OTP for deleting the shop '{shop.shop_name}' is: {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.user.email],
            )
            return JsonResponse({"status": "success", "message": f"OTP sent to {request.user.email}."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": "Failed to send OTP. Please try again."})

    elif request.method == "POST":
        # Handle OTP validation and shop deletion
        otp = request.POST.get("otp")
        if shop.shop_email in otp_storage and otp_storage[shop.shop_email] == otp:
            shop.delete()
            del otp_storage[shop.shop_email]
            messages.success(request, f"Shop '{shop.shop_name}' deleted successfully.")
            return redirect('overall_shop_list')
        else:
            # return JsonResponse({"status": "error", "message": "Invalid to send OTP"})
            messages.error(request, f"Invalid OTP")
            return redirect('update_shop',shop_id=shop_id)

    return redirect('update_shop',shop_id=shop_id)

@login_required
def shop_list(request):
    shops = Shop.objects.filter(user_id=request.user)

    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES)
        if form.is_valid():
            shop = form.save(commit=False)  # Create a shop instance without saving
            shop.user = request.user  # Set the user
            shop.save()  # Now save the shop
            messages.success(request, 'Shop created successfully.')
            return redirect('overall_shop_list')
    else:
        form = ShopForm()

    for shop in shops:
        shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)  # Encode UUID

    context = {
        'shops': shops,
        'form': form,
    }
    return render(request, 'tables/shop/shop_list.html', context)

@login_required
def shop_profile(request, shop_id):
    user_filter = {'user':request.user, 'shop_id':decode_base64_to_uuid(shop_id)}
    shop = get_object_or_404(Shop, **user_filter)

    user_shops = Shop.objects.filter(**user_filter)
    user_products = Product.objects.filter(**user_filter)
    stock_totals = Stock.objects.filter(**user_filter).order_by('date')

    print(stock_totals)
    total_employees = Employee.objects.filter().count()
    total_shifts = Shift.objects.filter(**user_filter).count()
    total_sales = Sale.objects.filter(**user_filter).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_expenses = Expense.objects.filter(**user_filter).aggregate(Sum('amount'))['amount__sum'] or 0
    profits_data = Profit.objects.filter(**user_filter).aggregate(
        total_gross=Sum('gross_profit'),
        total_net=Sum('net_profit'),
        total_loss=Sum('loss'),
        total_shortage=Sum('shortage')
    )

    profits = Profit.objects.filter(**user_filter).order_by('date')
    for profit in profits:
        profit.encoded_profit_id = encode_uuid_to_base64(profit.profit_id)
        
    shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)
    # If shop_id is provided, decode and filter by it
    
    if request.method == 'POST':
        form = ProfitForm(request.POST,shop=shop)
        if form.is_valid():
            profit = form.save(commit=False)  # Create a shop instance without saving
            profit.user = request.user  # Set the user
            profit.shop = shop  # Set the user
            profit.save()  # Now save the shop
            messages.success(request, 'Profit Record Create successfully.')
            return redirect('profits_dashboard',shop_id=shop_id)
    else:
        form = ProfitForm(shop=shop)
        
    # Pass data to the template
    context = {
        'total_shops': user_shops.count(),
        'total_products': user_products.count(),
        'total_stocks': stock_totals.count(),
        'total_employees': total_employees,
        'total_shifts': total_shifts,
        'total_sales': total_sales,
        'total_expenses': total_expenses,
        'total_gross_profits': profits_data['total_gross'] or 0,
        'total_net_profits': profits_data['total_net'] or 0,
        'total_losses': profits_data['total_loss'] or 0,
        'total_shortage': profits_data['total_shortage'] or 0,
        'profits': profits,
        'shop': shop,
        'form':form
    }
    return render(request, 'dashboard/shop_dashboard.html', context)

# ^  Shop end


# ^  employee Start
@login_required
def create_employee(request,shop_id):
    shop = get_object_or_404(Shop,  shop_id = decode_base64_to_uuid(shop_id), user=request.user)
    shop.encoded_shop_id = shop_id
    if not shop:
        return render(request, 'forms/shop/shop_form.html', {'error': 'No shop found for the current user.'})

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.user = request.user  # Set the owner as the creator
            employee.shop = shop  # Set the owner as the creator
            employee.save()
            return redirect('employee_list',shop_id=shop_id)  # Redirect to a list of employees or similar
    else:
        form = EmployeeForm()
    return render(request, 'forms/employee/employee_form.html', {'form': form, 'shop':shop})


@login_required
def update_employee(request,shop_id,employee_id):
    employee = get_object_or_404(Employee, employee_id=decode_base64_to_uuid(employee_id),shop_id = decode_base64_to_uuid(shop_id), user=request.user) 

    context = {}
    if shop_id:
       
        shop = get_object_or_404(Shop,  shop_id = decode_base64_to_uuid(shop_id), user=request.user)
        shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)
     
        context['shop'] = shop

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list',shop_id=shop_id)
    else:
        form = EmployeeForm(instance=employee)  

    context.update({'form': form, 'employee': employee})
    return render(request, 'forms/employee/employee_form.html', context)

@login_required
def delete_employee(request, shop_id, employee_id):
    # Decode base64 ids
    shop_uuid = decode_base64_to_uuid(shop_id)
    employee_uuid = decode_base64_to_uuid(employee_id)
    employee = get_object_or_404(Employee, employee_id=employee_uuid, shop_id=shop_uuid, user=request.user)
    
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully.')
    else:
        messages.error(request, 'Invalid request method.')

    return redirect('employee_list', shop_id=shop_id)

@login_required
def employee_list(request, shop_id=None):
    user_filter = {'user': request.user}
    context = {}

    if shop_id:
        shop_uuid = decode_base64_to_uuid(shop_id)
        user_filter['shop_id'] = shop_uuid

        shop = get_object_or_404(Shop, **user_filter)
        shop.encoded_shop_id = shop_id  # use the encoded version directly
        context['shop'] = shop

    employees = Employee.objects.filter(**user_filter)
    for employee in employees:
        employee.encoded_employee_id = encode_uuid_to_base64(employee.employee_id)

    context['employees'] = employees
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save(commit=False)  # Create a shop instance without saving
            employee.user = request.user  # Set the user
            employee.shop = shop  # Set the user
            employee.save()  # Now save the shop
            messages.success(request, 'Employee created successfully.')
            return redirect('employee_list',shop_id=shop_id)
    else:
        form = EmployeeForm()

    context['form'] = form
    return render(request, 'tables/employee/employee_list.html', context)

# ^  employee end

# ^  Shift Start
@login_required
def create_shift(request, shop_id=None):
    # Decode the shop ID and fetch the shop instance
    shop = Shop.objects.filter(shop_id=decode_base64_to_uuid(shop_id), user=request.user)
    shop.encoded_shop_id = encode_uuid_to_base64(shop.first().shop_id)
    
    context = {'shop': shop}

    # Handle form submission
    if request.method == 'POST':
        form = ShiftForm(request.POST, shop=shop.first())  # Pass the shop instance to the form
        if form.is_valid():
            shift = form.save(commit=False)
            shift.user = request.user  # Set the current user
            shift.shop = shop.first()  # Assign the shop instance
            shift.save()  # Save the shift to the database
            form.save_m2m()  # Save any many-to-many relationships
            return redirect('shift_list', shop_id=shop_id)  # Redirect to the shift list page
    else:
        form = ShiftForm(shop=shop.first())  # Pass the shop instance to the form for GET requests

    context['form'] = form
    return render(request, 'forms/shop/shift_form.html', context)

@login_required
def update_shift(request,shop_id, shift_id):
    # Decode the shop and shift IDs
    decoded_shop_id = decode_base64_to_uuid(shop_id)
    decoded_shift_id = decode_base64_to_uuid(shift_id)
    
    # Fetch Shift and Shop instances
    shift = get_object_or_404(Shift, shop_id=decoded_shop_id, shift_id=decoded_shift_id, user=request.user)
    shop = get_object_or_404(Shop, shop_id=decoded_shop_id, user=request.user)
    shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)

    # Initialize context with shop
    context = {'shop': shop, 'shift': shift}

    # Handle form submission
    if request.method == 'POST':
        form = ShiftForm(request.POST, shop=shop,instance=shift)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shift Updated successfully.')
            return redirect('shift_list', shop_id=shop_id)  # Redirect after successful update
    else:
        form = ShiftForm(shop=shop,instance=shift)  # Initialize form with existing shift data

    context['form'] = form
    return render(request, 'forms/shop/shift_form.html', context)

@login_required
def delete_shift(request,shop_id, shift_id):
    shift = get_object_or_404(Shift,shop_id=decode_base64_to_uuid(shop_id), shift_id=decode_base64_to_uuid(shift_id), user=request.user) 
    if request.method == 'POST':
        shift.delete()
        messages.success(request, 'Shift deleted successfully.')
    else:
        messages.error(request, 'Invalid request method.')

    return redirect('shift_list',shop_id=shop_id)  # Redirect after deletion

@login_required
def shift_list(request,shop_id=None,shift_id=None):
    user_filter = {'user': request.user}
    print(shift_id)
    context = {}

    if shop_id:
        shop_uuid = decode_base64_to_uuid(shop_id)
        user_filter['shop_id'] = shop_uuid

        shop = get_object_or_404(Shop, **user_filter)
        shop.encoded_shop_id = shop_id
     
        context['shop'] = shop

    shifts = Shift.objects.filter(**user_filter)

    for shift in shifts:
        shift.encoded_shift_id = encode_uuid_to_base64(shift.shift_id)  # Encode UUID
  
    print(shifts)
    
    context = {'shop': shop}

    shop = Shop.objects.filter(shop_id=decode_base64_to_uuid(shop_id), user=request.user)
    # Handle form submission
    if request.method == 'POST':
        form = ShiftForm(request.POST, shop=shop.first())  # Pass the shop instance to the form
        if form.is_valid():
            shift = form.save(commit=False)
            shift.user = request.user  # Set the current user
            shift.shop = shop.first()  # Assign the shop instance
            shift.save()  # Save the shift to the database
            form.save_m2m()  # Save any many-to-many relationships
            messages.success(request, 'Shift created successfully.')
            return redirect('shift_list', shop_id=shop_id)  # Redirect to the shift list page
    else:
        form = ShiftForm(shop=shop.first())  # Pass the shop instance to the form for GET requests

    context['form'] = form
    context['shifts']=shifts 
    
    return render(request, 'tables/shop/shift_list.html', context)

# ^  Shift end

# ^  Product start
@login_required
def create_product(request,shop_id=None):
    shop = get_object_or_404(Shop,  shop_id = decode_base64_to_uuid(shop_id), user=request.user)
    shop.encoded_shop_id = shop_id
    if not shop:
        return render(request, 'forms/shop/shop_form.html', {'error': 'No shop found for the current user.'})

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Pass the shop to the form
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user  # Set the current user
            product.shop = shop  # Assign the shop instance
            
            product.save()  # Save the shift to the database
            return redirect('product_list')  
    else:
        form = ProductForm()  # Pass the shop to the form

    return render(request, 'forms/shop/products/product_form.html', {'form': form,'shop':shop})
    
@login_required
def update_product(request, shop_id=None,product_id=None):
    product = get_object_or_404(Product, product_id=decode_base64_to_uuid(product_id), user=request.user, shop_id=decode_base64_to_uuid(shop_id)) 
    context = {}
    if shop_id:
       
        shop = get_object_or_404(Shop,  shop_id = decode_base64_to_uuid(shop_id), user=request.user)
        shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)
     
        context['shop'] = shop

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list',shop_id=shop_id)  
    else:
        form = ProductForm(instance=product) 
    context.update({'form': form, 'product': product})
    return render(request, 'forms/shop/products/product_form.html',context)

@login_required
def delete_product(request, shop_id=None,product_id=None):
    product = get_object_or_404(Product, product_id=decode_base64_to_uuid(product_id),shop_id=decode_base64_to_uuid(shop_id), user=request.user) 
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
    else:
        messages.error(request, 'Invalid request method.')

    return redirect('product_list',shop_id=shop_id)  

@login_required
def product_list(request,shop_id=None):
    user_filter = {'user': request.user}
    context = {}

    if shop_id:
        shop_uuid = decode_base64_to_uuid(shop_id)
        user_filter['shop_id'] = shop_uuid

        shop = get_object_or_404(Shop, **user_filter)
        shop.encoded_shop_id = shop_id
     
        context['shop'] = shop

    products = Product.objects.filter(**user_filter)
    context['products']=products

    for product in products:
        product.encoded_product_id = encode_uuid_to_base64(product.product_id)  # Encode UUID
        
    if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save(commit=False)  # Create a shop instance without saving
                product.user = request.user  # Set the user
                product.shop = shop  # Set the user
                product.save()  # Now save the shop
                return redirect('product_list',shop_id=shop_id)
    else:
            form = ProductForm()

    context['form'] = form
    
    return render(request, 'tables/shop/products/product_list.html', context)

# ^  Product end



# ^ Stocks Start

@login_required
def create_stock(request,shop_id=None):
    shop = get_object_or_404(Shop,  shop_id = decode_base64_to_uuid(shop_id), user=request.user)
    shop.encoded_shop_id = shop_id
    if not shop:
        return render(request, 'forms/shop/shop_form.html', {'error': 'No shop found for the current user.'})

    if request.method == 'POST':
        form = StockForm(request.POST,shop=shop)  # Pass the shop to the form
        if form.is_valid():
            stock = form.save(commit=False)
            stock.user = request.user  # Set the current user
            stock.shop = shop  # Assign the shop instance
            stock.save()  # Save the shift to the database
            return redirect('stock_list',shop_id=shop_id)  
    else:
        form = StockForm(shop=shop)  # Pass the shop to the form

    return render(request, 'forms/shop/products/stock_form.html', {'form': form, 'shop':shop})
    
@login_required
def update_stock(request, stock_id,shop_id=None):
    stock = get_object_or_404(Stock, stock_id=decode_base64_to_uuid(stock_id), user=request.user, shop_id=decode_base64_to_uuid(shop_id)) 
    context = {}
    if shop_id:
       
        shop = get_object_or_404(Shop,  shop_id = decode_base64_to_uuid(shop_id), user=request.user)
        shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)
     
        context['shop'] = shop    
    
    if request.method == 'POST':
        form = StockForm(request.POST,instance=stock)
        if form.is_valid():
            form.save()
            return redirect('stock_list',shop_id=shop_id)  # Redirect to the shop list page after update
    else:
        form = StockForm(instance=stock)  # Pre-fill the form with existing data

    context.update({'form': form, 'stock': stock})
    return render(request, 'forms/shop/products/stock_form.html',context)

@login_required
def delete_stock(request, stock_id,shop_id=None):
    stock = get_object_or_404(Stock, stock_id=decode_base64_to_uuid(stock_id),shop_id=decode_base64_to_uuid(shop_id), user=request.user) 
    if request.method == 'POST':
        stock.delete()
        messages.success(request, 'Stock deleted successfully.')
    else:
        messages.error(request, 'Invalid request method.')

    return redirect('stock_list',shop_id=shop_id)  

@login_required
def stock_list(request,shop_id=None):
    user_filter = {'user': request.user}
    context = {}

    if shop_id:
        shop_uuid = decode_base64_to_uuid(shop_id)
        user_filter['shop_id'] = shop_uuid

        shop = get_object_or_404(Shop, **user_filter)
        shop.encoded_shop_id = shop_id
     
        context['shop'] = shop

    stocks = Stock.objects.filter(**user_filter).order_by('-date')
    context['stocks']=stocks

    for stock in stocks:
        stock.encoded_stock_id = encode_uuid_to_base64(stock.stock_id)  # Encode UUID
        
    if request.method == 'POST':
            form = StockForm(request.POST,shop=shop)
            if form.is_valid():
                stock = form.save(commit=False)  # Create a shop instance without saving
                stock.user = request.user  # Set the user
                stock.shop = shop  # Set the user
                stock.save()  # Now save the shop
                return redirect('stock_list',shop_id=shop_id)
    else:
            form = StockForm(shop=shop)

    context['form'] = form
    context['total_stocks'] = stocks.count()
    
    return render(request, 'tables/shop/products/stock_list.html', context)

# ^ Stocks end


# ^  expense Type start
@login_required
def create_expense_type(request,shop_id=None):
    shop = get_object_or_404(Shop,  shop_id = decode_base64_to_uuid(shop_id), user=request.user)
    shop.encoded_shop_id = shop_id
    if not shop:
        return render(request, 'forms/shop/shop_form.html', {'error': 'No shop found for the current user.'})
    
    if request.method == 'POST':
        form = ExpenseTypeForm(request.POST,shop=shop)
        if form.is_valid():
            expenseType = form.save(commit=False)
            expenseType.user = request.user
            expenseType.shop = shop
            expenseType.save()
            return redirect('expense_type_list',shop_id=shop_id)  # Redirect to the list of expense types
    else:
        form = ExpenseTypeForm(shop=shop)
    return render(request, 'forms/finance/expense_type_form.html', {'form': form})


@login_required
def update_expense_type(request,shop_id, expense_type_id):
    expenseType = get_object_or_404(ExpenseType, expense_type_id=decode_base64_to_uuid(expense_type_id), user=request.user, shop_id=decode_base64_to_uuid(shop_id)) 
    context = {}
    if shop_id:
       
        shop = get_object_or_404(Shop,  shop_id = decode_base64_to_uuid(shop_id), user=request.user)
        shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)
     
        context['shop'] = shop    
    
    if request.method == 'POST':
        form = ExpenseTypeForm(request.POST,instance=expenseType)
        if form.is_valid():
            form.save()
            return redirect('expense_type_list',shop_id=shop_id)  # Redirect to the shop list page after update
    else:
        form = ExpenseTypeForm(instance=expenseType)  # Pre-fill the form with existing data

    context.update({'form': form, 'expenseType': expenseType})
    return render(request, 'forms/finance/expense_type_form.html', context)

@login_required
def delete_expense_type(request,shop_id, expense_type_id):
    expenseType = get_object_or_404(ExpenseType, expense_type_id=decode_base64_to_uuid(expense_type_id), user=request.user) 
    if request.method == 'POST':
        expenseType.delete()
        messages.success(request, 'Expense Type deleted successfully.')
    else:
        messages.error(request, 'Invalid request method.')

    return redirect('expense_type_list',shop_id=shop_id)  # Redirect after deletion

@login_required
def expense_type_list(request,shop_id):
    user_filter = {'user': request.user}
    context = {}

    if shop_id:
        shop_uuid = decode_base64_to_uuid(shop_id)
        user_filter['shop_id'] = shop_uuid

        shop = get_object_or_404(Shop, **user_filter)
        shop.encoded_shop_id = shop_id
     
        context['shop'] = shop
    expenseTypes = ExpenseType.objects.filter(**user_filter)

    for expenseType in expenseTypes:
        expenseType.encoded_expense_type_id = encode_uuid_to_base64(expenseType.expense_type_id)  # Encode UUID
     
    context['expenseTypes']=expenseTypes
    
    if request.method == 'POST':
            form = ExpenseTypeForm(request.POST,shop=shop)
            if form.is_valid():
                expenseType = form.save(commit=False)  # Create a shop instance without saving
                expenseType.user = request.user  # Set the user
                expenseType.shop = shop  # Set the user
                expenseType.save()  # Now save the shop
                return redirect('expense_type_list',shop_id=shop_id)
    else:
            form = ExpenseTypeForm(shop=shop)

    context['form'] = form
    
    return render(request, 'tables/finance/expense_type_list.html', context)

# ^  expense Type end


# ^  expense start
@login_required
def create_expense(request,shop_id):
    shop = Shop.objects.filter(user=request.user.user_id).first()  # Get the first shop for the logged-in user
    if not shop:
        return render(request, 'forms/shop/shop_form.html', {'error': 'No shop found for the current user.'})

    if request.method == 'POST':
        form = ExpenseForm(request.POST, shop=shop)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user  # Set the current user
            expense.shop = shop  # Assign the shop ID from the hidden input
            expense.save()  # Save the expense
            return redirect('expenses_dashboard',shop_id=shop_id)  # Redirect to expense list page
    else:
        form = ExpenseForm(shop=shop)  # Pass the user to the form
    return render(request, 'forms/finance/expense_form.html', {'form': form})

@login_required
def update_expense(request,shop_id, expense_id):
    expense = get_object_or_404(Expense, expense_id=decode_base64_to_uuid(expense_id), user=request.user, shop_id=decode_base64_to_uuid(shop_id)) 
    context = {}
    if shop_id:
        shop = get_object_or_404(Shop,  shop_id = decode_base64_to_uuid(shop_id), user=request.user)
        shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)
     
        context['shop'] = shop 
        
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense,shop=shop)
        if form.is_valid():
            form.save()
            return redirect('expenses_dashboard',shop_id=shop_id)  # Redirect to the shop list page after update
    else:
        form = ExpenseForm(instance=expense,shop=shop)  # Pre-fill the form with existing data
        
    context.update({'form': form, 'expense': expense})
    return render(request, 'forms/finance/expense_form.html', context)

@login_required
def delete_expense(request,shop_id, expense_id):
    expense = get_object_or_404(Expense, expense_id=decode_base64_to_uuid(expense_id),shop_id=decode_base64_to_uuid(shop_id), user=request.user) 
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense Record deleted successfully.')
    else:
        messages.error(request, 'Invalid request method.')

    return redirect('expenses_dashboard', shop_id=shop_id)

# @login_required
# def expense_list(request,shop_id=None):
#     user_filter = {'user': request.user}
#     context = {}

#     if shop_id:
#         shop_id = decode_base64_to_uuid(shop_id)
#         user_filter['shop_id'] = shop_id

#         shop = get_object_or_404(Shop, **user_filter)
#         shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)
     
#         context['shop'] = shop

#     expenses = Expense.objects.filter(**user_filter)
    #   for expense in expenses:
#         expenses.encoded_expense_id = encode_uuid_to_base64(expense.expense_id)  # Encode UUID


#     context['expenses'] = expenses

#     return render(request, 'tables/finance/expense_list.html', context)

# ^  expense end

# ^  sale start
@login_required
def create_sale(request,shop_id):
    shop = Shop.objects.filter(user=request.user)
    if not shop:
        return render(request, 'forms/shop/shop_form.html', {'error': 'No shop found for the current user.'})

    if request.method == 'POST':
        form = SaleForm(request.POST, shop=shop)
        if form.is_valid():
            Sale = form.save(commit=False)
            Sale.user = request.user  # Set the current user
            Sale.shop = shop  # Assign the shop ID from the hidden input
            Sale.save()  # Save the expense
            return redirect('sales_dashboard',shop_id=shop_id)  # Redirect to expense list page
    else:
        form = SaleForm(shop=shop)  # Pass the user to the form
    return render(request, 'forms/finance/sale_form.html', {'form': form})


@login_required
def update_sale(request,shop_id, sale_id):
    sale = get_object_or_404(Sale, sale_id=decode_base64_to_uuid(sale_id), user=request.user, shop_id=decode_base64_to_uuid(shop_id)) 
    context = {}
    if shop_id:
        shop = get_object_or_404(Shop,  shop_id = decode_base64_to_uuid(shop_id), user=request.user)
        shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)
     
        context['shop'] = shop
        
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale,shop=shop)
        if form.is_valid():
            form.save()
            return redirect('sales_dashboard',shop_id=shop_id)  # Redirect to the shop list page after update
    else:
        form = SaleForm(instance=sale,shop=shop)  # Pre-fill the form with existing data
    context.update({'form': form, 'sale': sale})
    return render(request, 'forms/finance/sale_form.html', context)

@login_required
def delete_sale(request,shop_id, sale_id):
    sale = get_object_or_404(Sale, sale_id=decode_base64_to_uuid(sale_id),shop_id=decode_base64_to_uuid(shop_id), user=request.user) 
    if request.method == 'POST':
        sale.delete()
        messages.success(request, 'Sale Record deleted successfully.')
    else:
        messages.error(request, 'Invalid request method.')

    return redirect('sales_dashboard',shop_id=shop_id)  


# @login_required
# def sale_list(request,shop_id=None):
#     user_filter = {'user': request.user}
    
#     context = {}

#     if shop_id:
#         shop_id = decode_base64_to_uuid(shop_id)
#         user_filter['shop_id'] = shop_id

#         shop = get_object_or_404(Shop, **user_filter)
#         shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)
     
#         context['shop'] = shop

#     sales = Sale.objects.filter(user_id=request.user).order_by('-date')
#     for sale in sales:
#         sale.encoded_sale_id = encode_uuid_to_base64(sale.sale_id)  # Encode UUID


#     context['sales']=sales


#     return render(request, 'tables/finance/sale_list.html', context)

# ^  sale end

# ^  Profit start
@login_required
def create_profit(request,shop_id):
    # Get the first shop associated with the logged-in user
    shop = get_object_or_404(Shop, shop_id=decode_base64_to_uuid(shop_id), user=request.user)

    if not shop:
        return render(request, 'forms/shop_form.html', {'error': 'No shop found for the current user.'})

    if request.method == 'POST':
        form = ProfitForm(request.POST, shop=shop)
        if form.is_valid():
            profit = form.save(commit=False)
            profit.user = request.user 
            profit.shop = shop  # Assign the shop
            profit.save()  # Save the profit record
            return redirect('profits_dashboard',shop_id=shop_id)  # Redirect to profit list page
    else:
        form = ProfitForm(shop=shop)  # Initialize an empty form

    return render(request, 'forms/finance/profit_form.html', {'form': form})

@login_required
def update_profit(request,shop_id, profit_id):
    # Ensure the user is associated with the profit
    profit = get_object_or_404(Profit, profit_id=decode_base64_to_uuid(profit_id), user=request.user, shop_id=decode_base64_to_uuid(shop_id))
    context = {}
    if shop_id:
        shop = get_object_or_404(Shop,  shop_id = decode_base64_to_uuid(shop_id), user=request.user)
        shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)
     
        context['shop'] = shop
        
    if request.method == 'POST':
        form = ProfitForm(request.POST, instance=profit)
        if form.is_valid():
            form.save()  # Save the updated profit record
            return redirect('profits_dashboard', shop_id=shop_id)  # Redirect to profit list page
    else:
        form = ProfitForm(instance=profit)
        
    context.update({'form': form, 'profit': profit})
    return render(request, 'forms/finance/profit_form.html', context)

@login_required
def delete_profit(request,shop_id, profit_id):
    profit = get_object_or_404(Profit, profit_id=decode_base64_to_uuid(profit_id),shop_id=decode_base64_to_uuid(shop_id), user=request.user) 
    if request.method == 'POST':
        profit.delete()
        messages.success(request, 'Profit Record deleted successfully.')
    else:
        messages.error(request, 'Invalid request method.')

    return redirect('profits_dashboard',shop_id=shop_id)  # Redirect after deletion


# @login_required
# def profit_list(request, shop_id=None):
#     # Base query for user and optional shop filter
#     user_filter = {'user': request.user}
    
#     context = {}

#     if shop_id:
#         shop_id = decode_base64_to_uuid(shop_id)
#         user_filter['shop_id'] = shop_id

#         shop = get_object_or_404(Shop, **user_filter)
#         shop.encoded_shop_id = encode_uuid_to_base64(shop.shop_id)
     
#         context['shop'] = shop

#     profits = Profit.objects.filter(user_id=request.user).order_by('-date')
#     for profit in profits:
#         profit.encoded_sale_id = encode_uuid_to_base64(profit.profit_id)  # Encode UUID
        
#     context['profits']=profits

#     return render(request, 'tables/finance/profit_list.html', context)

# ^  Profit end

# ^  dashboard start

@login_required
def dashboard_view(request, shop_id=None):
    # Base query for user and optional shop filter
    print("hello")
    user_filter = {'user': request.user}
    
    if shop_id:
        shop_id = decode_base64_to_uuid(shop_id)
        user_filter['shop_id'] = shop_id
        print(shop_id)
    
    # Aggregate common values
    total_shops = Shop.objects.filter(**user_filter).count()
    total_products = Product.objects.filter(**user_filter).count()
    total_employees = Employee.objects.filter(**user_filter).count()
    total_shifts = Shift.objects.filter(**user_filter).count()
    total_sales = Sale.objects.filter(**user_filter).aggregate(total_amount=Sum('total_amount'))['total_amount'] or 0
    total_expenses = Expense.objects.filter(**user_filter).aggregate(amount=Sum('amount'))['amount'] or 0
    total_gross_profits = Profit.objects.filter(**user_filter).aggregate(gross_profit=Sum('gross_profit'))['gross_profit'] or 0
    total_net_profits = Profit.objects.filter(**user_filter).aggregate(net_profit=Sum('net_profit'))['net_profit'] or 0
    total_losses = Profit.objects.filter(**user_filter).aggregate(loss=Sum('loss'))['loss'] or 0
    total_shortage = Profit.objects.filter(**user_filter).aggregate(shortage=Sum('shortage'))['shortage'] or 0
    print(total_shops)
    print(total_products)

    # Query profits with appropriate filters
    stocks = Stock.objects.filter(**user_filter).order_by('date')
    total_stocks = stocks.count()
    print(total_stocks)
    print(stocks)
    # Prepare data for JSON response
    data = {
        'total_shops': total_shops,
        'total_products': total_products,
        'total_employees': total_employees,
        'total_shifts': total_shifts,
        'total_sales': total_sales,
        'total_expenses': total_expenses,
        'total_gross_profits': total_gross_profits,
        'total_net_profits': total_net_profits,
        'total_losses': total_losses,
        'total_shortage': total_shortage,
        'total_stocks':total_stocks,
        'stocks': stocks
    }

    return render(request, 'dashboard/dashboard.html', data)

def dashboard_view1(request, template_name,type,shop_id=None, ):
    user_filter = {'user': request.user}
    shop = None
    
    # If shop_id is provided, decode and filter by it

    context = {}
    if shop_id:
        try:
            shop_uuid = decode_base64_to_uuid(shop_id)
            user_filter['shop_id'] = shop_uuid

            shop = get_object_or_404(Shop, **user_filter)
            shop.encoded_shop_id = shop_id
                    
        except Exception:
            pass
           
    form = None  # Initialize form to avoid UnboundLocalError

    if type ==  'sales':
        sales = Sale.objects.filter(**user_filter).order_by('date')
        for sale in sales:
            sale.encoded_sale_id = encode_uuid_to_base64(sale.sale_id)  # Encode UUID
            
        if request.method == 'POST':
            form = SaleForm(request.POST,shop=shop)
            if form.is_valid():
                sale = form.save(commit=False)  # Create a shop instance without saving
                sale.user = request.user  # Set the user
                sale.shop = shop  # Set the user
                sale.save()  # Now save the shop
                messages.success(request, 'Sale Record Create successfully.')
                return redirect('sales_dashboard',shop_id=shop_id)
        else:
            form = SaleForm(shop=shop)

        context['sales'] = sales
        
    if type ==  'expenses':
        expenses = Expense.objects.filter(**user_filter).order_by('date')
        for expense in expenses:
            expense.encoded_expense_id = encode_uuid_to_base64(expense.expense_id)  # Encode UUID   
            
        if request.method == 'POST':
            form = ExpenseForm(request.POST,shop=shop)
            if form.is_valid():
                expense = form.save(commit=False)  # Create a shop instance without saving
                expense.user = request.user  # Set the user
                expense.shop = shop  # Set the user
                expense.save()  # Now save the shop
                messages.success(request, 'Expense Record Create successfully.')
                return redirect('expenses_dashboard',shop_id=shop_id)
        else:
            form = ExpenseForm(shop=shop)          
                   
        context['expenses'] = expenses
        
    if type ==  'profits':
        profits = Profit.objects.filter(**user_filter).order_by('date')
        for profit in profits:
            profit.encoded_profit_id = encode_uuid_to_base64(profit.profit_id)  # Encode UUID
            
        if request.method == 'POST':
            form = ProfitForm(request.POST,shop=shop)
            if form.is_valid():
                profit = form.save(commit=False)  # Create a shop instance without saving
                profit.user = request.user  # Set the user
                profit.shop = shop  # Set the user
                profit.save()  # Now save the shop
                messages.success(request, 'Profit Record Create successfully.')
                return redirect('profits_dashboard',shop_id=shop_id)
        else:
            form = ProfitForm(shop=shop)
                
        context['profits'] = profits
        
    
    context['form'] = form
    print(context)
    
    # Get all shops that match the user filter
    shops = Shop.objects.filter(**user_filter)
    context.update({'shops': shops, 'shop': shop})
    return render(request, template_name,context)

def sales_dashboard(request, shop_id=None):
    
    return dashboard_view1(request, 'dashboard/sales_dashboard.html','sales', shop_id)

def expenses_dashboard(request, shop_id=None):
    return dashboard_view1(request, 'dashboard/expenses_dashboard.html','expenses', shop_id)

def profits_dashboard(request, shop_id=None):
    return dashboard_view1(request, 'dashboard/profits_dashboard.html','profits', shop_id)



# & Helper functions to prepare sales data for charts
def prepare_total_sales_over_time(sales_data):
    sales_over_time = sales_data.values('date').annotate(total_sales=Sum('total_amount')).order_by('date')
    return {
        'dates': [entry['date'] for entry in sales_over_time],
        'total_sales': [entry['total_sales'] for entry in sales_over_time],
    }

def prepare_product_sales(sales_data):
    product_sales = sales_data.values('product__name').annotate(total_sales=Sum('total_amount')).order_by('product__name')
    return {
        'product_names': [entry['product__name'] for entry in product_sales],
        'total_sales_by_product': [entry['total_sales'] for entry in product_sales],
    }

def prepare_shift_sales(sales_data):
    shift_sales = sales_data.values('shift__shift_name', 'shop__shop_name').annotate(total_sales=Sum('total_amount')).order_by('shift__shift_name')
    return {
        'shifts_names': [entry['shift__shift_name'] for entry in shift_sales],
        'total_sales_by_shift': [[entry['shop__shop_name'], entry['shift__shift_name'], entry['total_sales']] for entry in shift_sales],
    }

def prepare_shop_sales(sales_data):
    shop_sales = sales_data.values('shop__shop_name').annotate(total_sales=Sum('total_amount')).order_by('shop__shop_name')
    return {
        'shops_names': [entry['shop__shop_name'] for entry in shop_sales],
        'total_sales_by_shop': [entry['total_sales'] for entry in shop_sales],
    }

# Helper function to prepare data for a line/area chart over time
def prepare_time_series_data(queryset, group_by_fields, annotate_field='amount'):
    data = queryset.values(*group_by_fields).annotate(total=Sum(annotate_field)).order_by(*group_by_fields)
    structured_data = {}

    for entry in data:
        key = entry[group_by_fields[0]]
        if key not in structured_data:
            structured_data[key] = {field: [] for field in group_by_fields[1:]}
            structured_data[key]['totals'] = []
        
        for field in group_by_fields[1:]:
            structured_data[key][field].append(entry[field])
        structured_data[key]['totals'].append(entry['total'])

    return structured_data

def filter_sales_data(request,shop_id=None):
    filters = request.GET
    if not shop_id:
        shop_id = filters.get('shop_id')
    shift_id = filters.get('shift_id')
    year = filters.get('year')
    month = filters.get('month')
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    separate_shops = filters.get('separate_by_shop', '0') == '1'

    # Base queryset for sales data filtered by user
    sales_data = Sale.objects.filter(user=request.user)

    # Dynamic filtering
    filter_conditions = {}
    if shop_id:
        filter_conditions['shop_id'] = shop_id
    if shift_id:
        filter_conditions['shift_id'] = shift_id
    if year:
        filter_conditions['date__year'] = year
    if month:
        filter_conditions['date__month'] = month 
        
    # if end_date:
    #     end_date = parse_date(end_date)
    #     filter_conditions['date'] = end_date
    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        filter_conditions['date__range'] = [start_date, end_date]
                
    # Default date range if no filters are applied
    # if not filter_conditions:
    #     filter_conditions['date__range'] = [datetime.date(2024, 12, 1), datetime.date(2024, 12, 31)]

    # Apply filters
    sales_data = sales_data.filter(**filter_conditions)

    # Get sales data aggregated by date and shop name
    sales_over_time = sales_data.values('date', 'shop__shop_name').annotate(total_sales=Sum('total_amount')).order_by('date')

    # Structure data for plotting
    data_by_shop = {}
    for sale in sales_over_time:
        shop_name = sale['shop__shop_name']
        if shop_name not in data_by_shop:
            data_by_shop[shop_name] = {'date': [], 'sales': []}
        data_by_shop[shop_name]['date'].append(sale['date'])
        data_by_shop[shop_name]['sales'].append(sale['total_sales'])

    # Prepare data for different charts
    total_sales_over_time = prepare_total_sales_over_time(sales_data)
    total_sales_by_product = prepare_product_sales(sales_data)
    total_sales_by_shift = prepare_shift_sales(sales_data)
    total_sales_by_shop = prepare_shop_sales(sales_data)

    return JsonResponse({
        'data': data_by_shop,
        'separate_shops': separate_shops,
        **total_sales_over_time,
        **total_sales_by_product,
        **total_sales_by_shift,
        **total_sales_by_shop,
    }) 

def filter_expense_data(request,shop_id=None):
    filters = request.GET
    if not shop_id:
        shop_id = filters.get('shop_id')    
    type_id = filters.get('type_id')
    year = filters.get('year')
    month = filters.get('month')
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    separate_shops = request.GET.get('separate_by_shop', '0') == '1'

    # Base queryset for expenses
    expense_data = Expense.objects.filter(user=request.user)

      # Dynamic filtering
    filter_conditions = {}
    if shop_id:
        filter_conditions['shop_id'] = shop_id
    if type_id:
        filter_conditions['type_id'] = type_id
    if year:
        filter_conditions['date__year'] = year
    if month:
        filter_conditions['date__month'] = month
    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        filter_conditions['date__range'] = [start_date, end_date]
    
    # Default date range if no filters are applied
    # if not filter_conditions:
    #     filter_conditions['date__range'] = [datetime.date(2024, 12, 1), datetime.date(2024, 12, 31)]

    expense_data = expense_data.filter(**filter_conditions)

    expense_trends = expense_data.values('date','shop__shop_name').annotate(total_amount=Sum('amount')).order_by('date')

    # Structure data for plotting
    data_by_shop = {}
    for expense in expense_trends:
        shop_name = expense['shop__shop_name']
        # print(shop_name)
        if shop_name not in data_by_shop:
            data_by_shop[shop_name] = {'date': [], 'expenses': []}
        data_by_shop[shop_name]['date'].append(expense['date'])
        data_by_shop[shop_name]['expenses'].append(expense['total_amount'])
        
    # Expense trends over time (Line/Area Chart)
    expense_trends = expense_data.values('date').annotate(total_amount=Sum('amount')).order_by('date')
    dates = [entry['date'] for entry in expense_trends]
    total_amounts = [entry['total_amount'] for entry in expense_trends]

    # Expense breakdown by type (Donut Chart)
    expense_types = expense_data.values('type__name').annotate(total_amount=Sum('amount')).order_by('type__name')
    type_names = [entry['type__name'] for entry in expense_types]
    amounts_by_type = [entry['total_amount'] for entry in expense_types]

    # Expenses by shop (Stacked Bar Chart)
    shop_expenses = expense_data.values('shop__shop_name', 'type__name').annotate(total_amount=Sum('amount')).order_by('shop__shop_name', 'type__name')
    shops = list(set([entry['shop__shop_name'] for entry in shop_expenses]))
    expenses_by_shop = {}
    for shop in shops:
        expenses_by_shop[shop] = {entry['type__name']: entry['total_amount'] for entry in shop_expenses if entry['shop__shop_name'] == shop}

    return JsonResponse({
        'dates': dates,
        'data': data_by_shop,
        'total_amounts': total_amounts,
        'separate_shops': separate_shops,
        'type_names': type_names,
        'amounts_by_type': amounts_by_type,
        'expenses_by_shop': expenses_by_shop,
    })

def filter_profit_data(request, shop_id=None):
    print(shop_id)
    
    filters = request.GET
    if not shop_id:
        shop_id = filters.get('shop_id')
    year = filters.get('year')
    month = filters.get('month')
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    separate_shops = filters.get('separate_by_shop', '0') == '1'  # Separate data by shop

    # Filter profits based on user and other criteria
    profit_data = Profit.objects.filter(user=request.user)

        # Dynamic filtering
    filter_conditions = {}
    if shop_id:
        filter_conditions['shop_id'] = shop_id
    if year:
        filter_conditions['date__year'] = year
    if month:
        filter_conditions['date__month'] = month
    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)        
        filter_conditions['date__range'] = [start_date, end_date]
        
    # Default date range if no filters are applied
    # if not filter_conditions:
    #     filter_conditions['date__range'] = [datetime.date(2024, 12, 1), datetime.date(2024, 12, 31)]

    profit_data = profit_data.filter(**filter_conditions)

    if separate_shops:
        # Data for Line Chart - Gross and Net Profit Over Time
        profit_over_time = profit_data.values('date', 'shop__shop_name').annotate(
            gross_profit=Sum('gross_profit'),
            net_profit=Sum('net_profit')
        ).order_by('date')

        # Data for Monthly Comparison of Income vs. Expenses
        monthly_comparison = profit_data.values('date__month', 'shop__shop_name').annotate(
            total_income=Sum('total_income'),
            total_expenses=Sum('total_expenses')
        ).order_by('date__month')

        # Revenue and Expense Breakdown by Shop
        revenue_expenses = profit_data.values('shop__shop_name').annotate(
            total_income=Sum('total_income'),
            total_expenses=Sum('total_expenses'),
            cost_of_goods_sold=Sum('cost_of_goods_sold'),
            operating_expenses=Sum('operating_expenses')
        )

        # Data for Profit vs. Loss by Shop
        profit_vs_loss = profit_data.values('date', 'shop__shop_name').annotate(
            profit=F('gross_profit') - F('total_expenses') - F('operating_expenses'),
            loss=F('loss')
        ).order_by('date')

    else:
        # Without separating by shop
        profit_over_time = profit_data.values('date').annotate(
            gross_profit=Sum('gross_profit'),
            net_profit=Sum('net_profit')
        ).order_by('date')

        monthly_comparison = profit_data.values('date__month').annotate(
            total_income=Sum('total_income'),
            total_expenses=Sum('total_expenses')
        ).order_by('date__month')

        revenue_expenses = profit_data.aggregate(
            total_income=Sum('total_income'),
            total_expenses=Sum('total_expenses'),
            cost_of_goods_sold=Sum('cost_of_goods_sold'),
            operating_expenses=Sum('operating_expenses')
        )

        profit_vs_loss = profit_data.values('date').annotate(
            profit=F('gross_profit') - F('total_expenses') - F('operating_expenses'),
            loss=F('loss')
        ).order_by('date')

    # Structure data for JSON response
    return JsonResponse({
        'profit_over_time': list(profit_over_time),
        'monthly_comparison': list(monthly_comparison),
        'revenue_expenses': revenue_expenses if not separate_shops else list(revenue_expenses),
        'profit_vs_loss': list(profit_vs_loss),
        'separate_shops': separate_shops,
        
    })

# ^  dashboard end


# ^  ajax start

def ajax_get_shifts(request):
    shop_id = request.GET.get('shop_id')
    shifts = Shift.objects.filter(shop_id=shop_id).values('shift_id', 'shift_name') if shop_id else []
    return JsonResponse({'shifts': list(shifts)})

def ajax_get_expenseType(request):
    shop_id = request.GET.get('shop_id')
    shifts = ExpenseType.objects.filter(shop_id=shop_id).values('expense_type_id', 'name') if shop_id else []
    return JsonResponse({'ExpenseTypes': list(shifts)})

# ^  ajax end
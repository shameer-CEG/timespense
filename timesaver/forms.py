from django import forms
from django.contrib.auth.forms import UserCreationForm,SetPasswordForm,PasswordChangeForm
from .models import *
from crispy_forms.helper import FormHelper
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from crispy_forms.layout import Layout, Field, Submit, Row, Column,Fieldset
import datetime  

PAYMENT_METHOD_CHOICES = [
    ('Cash', 'Cash'),
    ('Credit Card', 'Credit Card'),
    ('Debit Card', 'Debit Card'),
    ('Online Payment', 'Online Payment'),
]

phone_number_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

# ^  Authentication start
class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'id': 'password-field'}))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('login', 'Log In', css_class='btn btn-primary'))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            raise forms.ValidationError("Invalid login credentials. Please try again.")

        cleaned_data['user'] = user
        return cleaned_data
        
    # Signup Form
class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )

    user_phone_number = forms.CharField(
        validators=[phone_number_validator],
        widget=forms.TextInput(attrs={
            'type': 'tel',
            'autocomplete': 'tel',  # Suggestion for autocomplete attribute
            'class': 'form-control',
            'placeholder': 'Enter phone number'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'user_phone_number']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'autocomplete': 'username', 
            'class': 'form-control'
        })

    # def __init__(self, *args, **kwargs):
    #     super(SignupForm, self).__init__(*args, **kwargs)
        # self.helper = FormHelper()
        # self.helper.form_method = 'post'
        # self.helper.add_input(Submit('signup', 'Sign Up', css_class='btn btn-primary'))
# ^  Authentication end

# ^  password recovery start

class CustomPasswordResetConfirmForm(SetPasswordForm):
    formSubmitted = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add 'form-control' class to new_password1 and new_password2 fields
        for field in ['new_password1', 'new_password2']:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

# ^  password recovery end

# ^ User start 

class UserForm(forms.ModelForm):
    # Phone number validation for user
    phone_number_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '999999999'. Up to 15 digits allowed."
    )

    user_phone_number = forms.CharField(
        validators=[phone_number_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'})
    )

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'user_phone_number', 'profile_image']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'opacity-0', 'style': 'display:none;', "onchange": "previewImage(event)"}),

        }

    # def __init__(self, *args, **kwargs):
    #     super(UserForm, self).__init__(*args, **kwargs)
    #     # Initialize FormHelper for crispy form styling
    #     # self.helper = FormHelper()
    #     # self.helper.form_method = 'post'
    #     # self.helper.add_input(Submit('user_form', 'Save', css_class='btn btn-primary mt-3'))

    #     # Add crispy class to each field for uniform styling
    #     for field in self.fields.values():
    #         field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.user_code:
            user.user_code = user.generate_custom_code()
        if commit:
            user.save()
        return user
    
# ^ user end

# ^  shop start

class ShopForm(forms.ModelForm):

    
    shop_phone_number = forms.CharField(
        validators=[phone_number_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'})
    )

    class Meta:
        
        model = Shop
        fields = ['shop_name','shop_address','shop_phone_number','shop_email','shop_image']  # Exclude 'user' from fields
        widgets = {
            'shop_email': forms.TextInput(attrs={'class': 'form-control'}),
            'shop_name': forms.TextInput(attrs={'class': 'form-control'}),
            'shop_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'shop_address': forms.Textarea(attrs={'class': 'form-control'}),
            'shop_image': forms.ClearableFileInput(attrs={'class': 'opacity-0', 'style': 'display:none;', "onchange": "previewImage(event)"}),

            # 'shop_image': forms.ClearableFileInput(attrs={'class': 'opacity-0',"onchange":"previewImage(event)"}),
        }

    # def __init__(self, *args, **kwargs):
    #     self.user = kwargs.pop('user', None)  # Get user from kwargs
    #     super().__init__(*args, **kwargs)
    #     self.helper = FormHelper()
    #     self.helper.form_method = 'post'
    #     self.helper.add_input(Submit('shop_form', 'Save', css_class='btn btn-primary'))

    def save(self, commit=True):
        shop = super().save(commit=False)
        if not shop.shop_code:
            shop.shop_code = shop.generate_custom_code()
        if commit:
            shop.save()
        return shop
    
# ^  shop end
    
# ^  employee start
class EmployeeForm(forms.ModelForm):
    phone_number_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

    phone_number = forms.CharField(
        validators=[phone_number_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'})
    )
    class Meta:
        model = Employee
        fields = [
            'name', 'email', 'phone_number', 'address', 
            'role', 'employee_image'
        ]
        widgets = {
            # 'employee_image': forms.ClearableFileInput(attrs={'class': 'form-control btn ','type':"file", "onchange":"previewImage(event)"}),
               'employee_image': forms.ClearableFileInput(attrs={'class': 'opacity-0', 'style': 'display:none;', "onchange": "previewImage(event)"}),
        }

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)

    
 
# ^  employee end

# ^  shift start
class ShiftForm(forms.ModelForm):
    shift_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Shift Name',
            'class': 'form-control',  # Bootstrap 5 class for input fields
        }),
        label='Shift Name'
    )
    start_time = forms.DateTimeField(
        initial=timezone.now,  # Sets the current date and time
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',  # Bootstrap 5 class for input fields
        }),
        label='Start Date & Time'
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',  # Bootstrap 5 class for input fields
        }),
        label='End Date & Time'
    )

    class Meta:
        model = Shift
        fields = ['shift_name', 'start_time', 'end_time', 'employees']

    def __init__(self, *args, shop=None, **kwargs):
        super(ShiftForm, self).__init__(*args, **kwargs)

        if isinstance(shop, Shop):
            self.fields['employees'] = forms.ModelMultipleChoiceField(
                queryset=Employee.objects.filter(shop=shop),
                
                required=False,
                label='Employees'
            )

        # Crispy form helper to enhance the form layout
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('shift_name', css_class='mb-3'),
            Row(
                Column(Field('start_time', css_class='mb-3'), css_class='col-md-6'),
                Column(Field('end_time', css_class='mb-3'), css_class='col-md-6'),
            ),
            Field('employees', css_class='mb-3'),
            Submit('submit', 'Save Shift', css_class='btn btn-primary ')
        )
# ^  shift end

# ^  product start
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price_per_unit', 'unit', 'product_image']
        widgets = {
            # 'product_image': forms.ClearableFileInput(attrs={'class': 'form-control',"onchange":"previewImage(event)"}),
                        'product_image': forms.ClearableFileInput(attrs={'class': 'opacity-0', 'style': 'display:none;', "onchange": "previewImage(event)"}),

        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save', css_class='btn btn-primary'))
# ^  product end

# ^ stock start

class StockForm(forms.ModelForm):
    # Custom validation for stock quantities (ensures all quantities are non-negative)
    opening_stock = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Opening stock'}))
    added_stock = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Added stock'}))
    sold_quantity = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Sold quantity'}))

    class Meta:
        model = Stock
        fields = ['product', 'date', 'opening_stock', 'added_stock', 'sold_quantity']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'closing_stock': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def __init__(self, *args,shop=None, **kwargs):
        super(StockForm, self).__init__(*args, **kwargs)
        if isinstance(shop, Shop):
                self.fields['product'] = forms.ModelChoiceField(
                queryset=Product.objects.filter(shop=shop),
                widget=forms.Select(attrs={'class': 'form-control'})
            )

        # Initialize FormHelper for crispy form styling
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('stock_form', 'Save', css_class='btn btn-primary mt-3'))
        
        # Add crispy class to every field for uniform styling
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
# ^ stock end

# ^  Expenses and types start
class ExpenseTypeForm(forms.ModelForm):
    class Meta:
        model = ExpenseType
        fields = ['name']

    def __init__(self, *args,shop=None, **kwargs):
        super(ExpenseTypeForm, self).__init__(*args, **kwargs)
       
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save', css_class='btn btn-primary'))

class ExpenseForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Date'
    )

    class Meta:
        model = Expense
        fields = ['date', 'type', 'amount', 'description', 'payment_method']

    def __init__(self, *args, shop=None, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        
        # Set default date to today's date
        self.fields['date'].initial = datetime.date.today()
        
        # Dynamically filter 'type' based on shop if provided
        if shop:
            self.fields['type'] = forms.ModelChoiceField(
                queryset=ExpenseType.objects.filter(shop=shop.shop_id),  # Fetch expense types dynamically for the given shop
                widget=forms.Select(attrs={'class': 'form-control'}),
                required=True  # Make this field required
            )
        
        # Add crispy form classes to fields for better styling
        self.fields['amount'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter amount'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'rows': 3, 'placeholder': 'Description (optional)'})
        self.fields['payment_method'].widget = forms.Select(
            choices=PAYMENT_METHOD_CHOICES,
            attrs={'class': 'form-control'}
        )
        
        # Initialize crispy form helper for styling and submission
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save', css_class='btn btn-primary'))

# ^  Expenses and types end

# ^  sale start

class SaleForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Date'
    )

    class Meta:
        model = Sale
        fields = ['date', 'product', 'quantity', 'total_amount', 'shift', 'payment_method']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total Amount'}),
        }

    def __init__(self, *args, shop=None, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        
        # Set default date to today's date
        self.fields['date'].initial = datetime.date.today()
        
        # Dynamically filter 'product' field based on shop if provided
        if shop:
            self.fields['product'] = forms.ModelChoiceField(
                queryset=Product.objects.filter(shop=shop.shop_id),  # Fetch products for the given shop
                widget=forms.Select(attrs={'class': 'form-control'}),
                required=True
            ) 
            self.fields['shift'] = forms.ModelChoiceField(
                queryset=Shift.objects.filter(shop=shop.shop_id),  # Fetch products for the given shop
                widget=forms.Select(attrs={'class': 'form-control'}),
                required=True
            )
        
        # Add crispy form classes for better styling
        self.fields['quantity'].widget.attrs.update({'class': 'form-control'})
        self.fields['total_amount'].widget.attrs.update({'class': 'form-control'})
        self.fields['shift'].widget.attrs.update({'class': 'form-control'})
        self.fields['payment_method'].widget = forms.Select(
            choices=PAYMENT_METHOD_CHOICES,
            attrs={'class': 'form-control'}
        )
        

        # Initialize crispy form helper for layout and submission
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save', css_class='btn btn-primary'))


# ^  sale end


# ^  Profit start
class ProfitForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Date'
    )

    class Meta:
        model = Profit
        fields = ['date', 'total_income', 'total_expenses', 'cost_of_goods_sold', 'operating_expenses']
        widgets = {
            'total_income': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total Income'}),
            'total_expenses': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total Expenses'}),
            'cost_of_goods_sold': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cost of Goods Sold'}),
            'operating_expenses': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Operating Expenses'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, shop=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user  # Store the user passed to the form
        self.fields['date'].initial = datetime.date.today()  # Set initial date to today

        # Initialize crispy form helper for layout and submission
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save', css_class='btn btn-primary'))

    def clean(self):
        cleaned_data = super().clean()
        
        # Perform the profit calculations in the form (based on the model's save logic)
        total_income = cleaned_data.get('total_income')
        total_expenses = cleaned_data.get('total_expenses')
        cost_of_goods_sold = cleaned_data.get('cost_of_goods_sold')
        operating_expenses = cleaned_data.get('operating_expenses')

        gross_profit = total_income - cost_of_goods_sold
        net_profit = gross_profit - operating_expenses - total_expenses
        shortage = total_expenses - total_income if total_expenses > total_income else 0
        loss = abs(net_profit) if net_profit < 0 else 0

        # Add the calculated values to the cleaned data
        cleaned_data['gross_profit'] = gross_profit
        cleaned_data['net_profit'] = net_profit
        cleaned_data['shortage'] = shortage
        cleaned_data['loss'] = loss
        
        return cleaned_data

    def save(self, commit=True):
        # Save the profit form and return the instance
        profit = super().save(commit=False)
        
        # If commit is True, save the Profit instance
        if commit:
            profit.save()
        
        return profit


# ^  profit end

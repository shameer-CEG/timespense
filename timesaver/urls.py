from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [

    
    # & Password Reset/Recovery
    path('forgotpwd/', CustomPasswordResetView.as_view(), name='password'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('shop/<str:shop_id>/user/change-password/', change_password_view, name='shop_change_password'),
    path('user/change-password/', change_password_view, name='change_password'),
    
    # & Stock URLs (commented lines can be similarly added if needed)
    path('shop/<str:shop_id>/user/update/', update_user, name='shop_update_user'),
    path('user/update/', update_user, name='update_user'),
    path('user/delete/', delete_user, name='delete_user'),

    # & Shop CRUD
    path('shop/create/', create_shop, name='create_shop'),
    path('shops/', shop_list, name='overall_shop_list'),
    path('shop/<str:shop_id>/', shop_profile, name='shop_profile'),
    path('shop/<str:shop_id>/update/', update_shop, name='update_shop'),
    path('shop/<str:shop_id>/delete/', delete_shop, name='delete_shop'),

    # & Employee CRUD
    path('<str:shop_id>/employees/', employee_list, name='employee_list'),
    path('<str:shop_id>/employee/update/<str:employee_id>', update_employee, name='update_employee'),
    path('employees/', employee_list, name='overall_employee_list'), 
    path('<str:shop_id>/employee/create/', create_employee, name='create_employee'),
    path('<str:shop_id>/employee/<str:employee_id>/delete/', delete_employee, name='delete_employee'),

    # & Product CRUD
    path('<str:shop_id>/products/', product_list, name='product_list'),
    path('products/', product_list, name='overall_product_list'),  
    path('<str:shop_id>/product/create/', create_product, name='create_product'),
    path('<str:shop_id>/product/<str:product_id>/update/', update_product, name='update_product'),
    path('<str:shop_id>/product/<str:product_id>/delete/', delete_product, name='delete_product'),

    # & Stock URLs (commented lines can be similarly added if needed)
    path('<str:shop_id>/stock/', stock_list, name='stock_list'),
    path('<str:shop_id>/stock/create/', create_stock, name='create_stock'),
    path('<str:shop_id>/stock/update/<str:stock_id>/', update_stock, name='update_stock'),
    path('<str:shop_id>/stock/delete/<str:stock_id>/', delete_stock, name='delete_stock'),

    # & Shift URLs
    path('<str:shop_id>/shifts/<str:shift_id>/', shift_list, name='shift_list'),
    path('<str:shop_id>/shifts/', shift_list, name='shift_list'),
    
    path('<str:shop_id>/shift/create/', create_shift, name='create_shift'),
    path('<str:shop_id>/shift/update/<str:shift_id>/', update_shift, name='update_shift'),
    path('<str:shop_id>/shift/delete/<str:shift_id>/', delete_shift, name='delete_shift'),

    # & Expense Type URLs
    path('<str:shop_id>/expense-types/', expense_type_list, name='expense_type_list'),
    path('expense-types/', expense_type_list, name='overall_expense_type_list'), 
    path('<str:shop_id>/expense-type/create/', create_expense_type, name='create_expense_type'),
    path('<str:shop_id>/expense-type/<str:expense_type_id>/update/', update_expense_type, name='update_expense_type'),
    path('<str:shop_id>/expense-type/<str:expense_type_id>/delete/', delete_expense_type, name='delete_expense_type'),

    # & Expense URLs
    # path('<str:shop_id>/expenses/', expense_list, name='expense_list'),
    # path('expenses/', expense_list, name='overall_expense_list'), 
    path('<str:shop_id>/expense/create/', create_expense, name='create_expense'),
    path('<str:shop_id>/expense/update/<str:expense_id>/', update_expense, name='update_expense'),
    path('<str:shop_id>/expense/delete/<str:expense_id>/', delete_expense, name='delete_expense'),

    # & Sale URLs
    # path('<str:shop_id>/sales/', sale_list, name='sale_list'),
    # path('sales/', sale_list, name='overall_sale_list'),  
    path('<str:shop_id>/sale/create/', create_sale, name='create_sale'),
    path('<str:shop_id>/sale/update/<str:sale_id>/', update_sale, name='update_sale'),
    path('<str:shop_id>/sale/delete/<str:sale_id>/', delete_sale, name='delete_sale'),
    
    # & Profit URLs
    # path('<str:shop_id>/profits/', profit_list, name='profit_list'),  
    # path('profits/', profit_list, name='overall_profit_list'), 
    path('<str:shop_id>/profit/create/', create_profit, name='create_profit'),
    path('<str:shop_id>/profit/update/<str:profit_id>/', update_profit, name='update_profit'),
    path('<str:shop_id>/profit/delete/<str:profit_id>/', delete_profit, name='delete_profit'),

    # & Dashboard URLs
    # path('<str:shop_id>/dashboard/', dashboard_view, name='dashboard'),  
    path('dashboard/', dashboard_view, name='overall_dashboard'),  

    # & Dashboard analytics views    
    path('<str:shop_id>/dashboard/sales-chart/', sales_dashboard, name='sales_dashboard'),
    path('<str:shop_id>/dashboard/expenses-chart/', expenses_dashboard, name='expenses_dashboard'),
    path('<str:shop_id>/dashboard/profits-chart/', profits_dashboard, name='profits_dashboard'),

    path('dashboard/sales-chart/', sales_dashboard, name='overall_sales_dashboard'),
    path('dashboard/expenses-chart/', expenses_dashboard, name='overall_expenses_dashboard'),
    path('dashboard/profits-chart/', profits_dashboard, name='overall_profits_dashboard'),
    
    path('dashboard/filter_sales_data/<str:shop_id>/', filter_sales_data, name='filter_sales_data'),
    path('dashboard/filter_expenses_data/<str:shop_id>/', filter_expense_data, name='filter_expenses_data'),
    path('dashboard/filter_profit_data/<str:shop_id>/', filter_profit_data, name='filter_profit_data'),
    
    path('dashboard/filter_sales_data/', filter_sales_data, name='filter_sales_data'),
    path('dashboard/filter_expenses_data/', filter_expense_data, name='filter_expenses_data'),
    path('dashboard/filter_profit_data/', filter_profit_data, name='filter_profit_data'),

    # & AJAX endpoints for dashboard data
    path('dashboard/ajax_get_shifts/', ajax_get_shifts, name='ajax_get_shifts'),
    path('dashboard/ajax_get_expense_type/', ajax_get_expenseType, name='ajax_get_expenseType'),


    # & User Signup/Login
    path('signup/', signup_view, name='signup'),
    path('', login_view, name='login'),

    # & Employee Login
    # path('employee-login/', employee_login_view, name='login_employee'),

    # & Logout
    path('logout/', logout_view, name='logout'),


]

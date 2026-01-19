from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('simulate/', views.simulate_alert, name='simulate_alert'),
    path('settings/', views.settings, name='settings'),
    path('settings/wallet/add/', views.wallet_create, name='wallet_create'),
    path('settings/distribution/add/', views.distribution_create, name='distribution_create'),
    path('settings/bank/update/', views.bank_account_update, name='bank_account_update'),

    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/edit/', views.transaction_update, name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('reports/', views.dashboard, name='reports'), # Placeholder
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    
    # Payslips
    path('payslips/', views.payslip_list, name='payslip_list'),
    path('payslips/add/', views.payslip_create, name='payslip_create'),
    path('payslips/<int:pk>/pdf/', views.payslip_pdf, name='payslip_pdf'),

    # Invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/add/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
]

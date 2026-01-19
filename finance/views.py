from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Transaction, Payslip, Invoice, Wallet, DistributionSetting, BankAccount
from .forms import TransactionForm, PayslipForm, InvoiceForm, SimulateAlertForm, WalletForm, DistributionSettingForm, BankAccountForm
from .utils import distribute_income
import openpyxl

@login_required
def dashboard(request):
    wallets = Wallet.objects.filter(user=request.user)
    recent_transactions = Transaction.objects.filter(created_by=request.user).order_by('-date')[:5]
    
    context = {
        'wallets': wallets,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'finance/dashboard.html', context)

@login_required
def simulate_alert(request):
    if request.method == 'POST':
        form = SimulateAlertForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            distribute_income(request.user, amount)
            return redirect('dashboard')
    else:
        form = SimulateAlertForm()
    return render(request, 'finance/generic_form.html', {
        'form': form,
        'title': 'Simulate Bank Alert',
        'back_url': 'dashboard'
    })

@login_required
def settings(request):
    user = request.user
    try:
        bank_account = BankAccount.objects.get(user=user)
    except BankAccount.DoesNotExist:
        bank_account = None

    wallets = Wallet.objects.filter(user=user)
    distribution_settings = DistributionSetting.objects.filter(user=user)
    
    return render(request, 'finance/settings.html', {
        'bank_account': bank_account,
        'wallets': wallets,
        'distribution_settings': distribution_settings
    })

@login_required
def wallet_create(request):
    if request.method == 'POST':
        form = WalletForm(request.POST)
        if form.is_valid():
            wallet = form.save(commit=False)
            wallet.user = request.user
            wallet.save()
            return redirect('settings')
    else:
        form = WalletForm()
    return render(request, 'finance/generic_form.html', {'form': form, 'title': 'Add Wallet', 'back_url': 'settings'})

@login_required
def distribution_create(request):
    if request.method == 'POST':
        form = DistributionSettingForm(request.POST)
        if form.is_valid():
            unique_check = DistributionSetting.objects.filter(user=request.user, wallet=form.cleaned_data['wallet']).exists()
            if unique_check:
                 form.add_error('wallet', 'Rule for this wallet already exists.')
            else:
                setting = form.save(commit=False)
                setting.user = request.user
                setting.save()
                return redirect('settings')
    else:
        form = DistributionSettingForm()
        form.fields['wallet'].queryset = Wallet.objects.filter(user=request.user)
        
    return render(request, 'finance/generic_form.html', {'form': form, 'title': 'Add Distribution Rule', 'back_url': 'settings'})

@login_required
def bank_account_update(request):
    try:
        bank_account = BankAccount.objects.get(user=request.user)
    except BankAccount.DoesNotExist:
        bank_account = None
        
    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=bank_account)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            return redirect('settings')
    else:
        form = BankAccountForm(instance=bank_account)
    return render(request, 'finance/generic_form.html', {'form': form, 'title': 'Update Bank Account', 'back_url': 'settings'})

@login_required
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-date')
    return render(request, 'finance/transaction_list.html', {'transactions': transactions})

@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.created_by = request.user
            transaction.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'finance/transaction_form.html', {'form': form})

@login_required
def transaction_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'finance/transaction_form.html', {'form': form})

@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        return redirect('transaction_list')
    return render(request, 'finance/transaction_confirm_delete.html', {'object': transaction})

@login_required
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="transactions.xlsx"'
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Transactions"
    
    headers = ['Date', 'Type', 'Category', 'Description', 'Amount', 'Created By']
    ws.append(headers)
    
    transactions = Transaction.objects.all()
    for t in transactions:
        ws.append([t.date, t.type, t.category, t.description, t.amount, t.created_by.username if t.created_by else 'N/A'])
        
    wb.save(response)
    return response

@login_required
def export_pdf(request):
    transactions = Transaction.objects.all().order_by('-date')
    
    # Calculate totals for the report
    total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    net_balance = total_income - total_expenses
    
    template_path = 'finance/transaction_pdf.html'
    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': net_balance,
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transaction_report.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
def reports(request):
    # Simple report view, can reuse dashboard or be more specific
    return render(request, 'finance/dashboard.html', {'report': True}) # Placeholder reuse

# Payslip Views
@login_required
def payslip_list(request):
    payslips = Payslip.objects.all().order_by('-month')
    return render(request, 'finance/payslip_list.html', {'payslips': payslips})

@login_required
def payslip_create(request):
    if request.method == 'POST':
        form = PayslipForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('payslip_list')
    else:
        form = PayslipForm()
    return render(request, 'finance/generic_form.html', {
        'form': form, 
        'title': 'Generate Payslip',
        'back_url': 'payslip_list'
    })

@login_required
def payslip_pdf(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    template_path = 'finance/payslip_pdf.html'
    context = {'payslip': payslip}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payslip_{payslip.employee_name}.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# Invoice Views
@login_required
def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-issue_date')
    return render(request, 'finance/invoice_list.html', {'invoices': invoices})

@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('invoice_list')
    else:
        form = InvoiceForm()
    return render(request, 'finance/generic_form.html', {
        'form': form, 
        'title': 'Create Invoice',
        'back_url': 'invoice_list'
    })

@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    template_path = 'finance/invoice_pdf.html'
    context = {'invoice': invoice}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.client_name}.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

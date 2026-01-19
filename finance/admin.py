from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Transaction, Payslip, Invoice, Wallet, DistributionSetting, BankAccount

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'role', 'is_staff',]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Transaction)
admin.site.register(Payslip)
admin.site.register(Invoice)
admin.site.register(Wallet)
admin.site.register(DistributionSetting)
admin.site.register(BankAccount)

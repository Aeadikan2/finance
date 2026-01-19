from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Wallet, DistributionSetting, Transaction

def distribute_income(user, amount, description="Bank Alert Simulation"):
    """
    Distributes the given amount into user's wallets based on defined percentages.
    """
    amount = Decimal(amount)
    settings = DistributionSetting.objects.filter(user=user)
    
    with transaction.atomic():
        distributed_total = Decimal(0)
        
        for setting in settings:
            wallet = setting.wallet
            percentage = setting.percentage
            split_amount = (amount * percentage) / Decimal(100)
            
            # Update wallet balance
            wallet.current_balance += split_amount
            wallet.save()
            
            # Log transaction
            Transaction.objects.create(
                type='income',
                category=wallet.name,
                amount=split_amount,
                description=f"{description} ({percentage}%)",
                date=timezone.now().date(),
                created_by=user
            )
            distributed_total += split_amount

        remainder = amount - distributed_total
        if remainder > Decimal('0.01'):
            # Find or create a 'Main' or 'Unallocated' wallet
            main_wallet = Wallet.objects.filter(user=user, name__in=['Main', 'Income', 'Main Balance']).first()
            if not main_wallet:
                main_wallet, created = Wallet.objects.get_or_create(user=user, name='Unallocated')
            
            main_wallet.current_balance += remainder
            main_wallet.save()
            
            Transaction.objects.create(
                type='income',
                category=main_wallet.name,
                amount=remainder,
                description=f"{description} (Remainder/Unallocated)",
                date=timezone.now().date(),
                created_by=user
            )

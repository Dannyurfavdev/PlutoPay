from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import *

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class Client(models.Model):
    user= models.OneToOneField(CustomUser, on_delete= models.CASCADE, null=True, blank=True)
    bio= models.TextField(max_length=764, null=True, blank=True)
    first_name= models.CharField(max_length=64, default="Update Your Account", null=True, blank=True)
    last_name= models.CharField(max_length=64, default="Update Your Account", null=True, blank=True)
    bank_name= models.CharField(max_length=64, default="Update Your Account", null=True, blank=True)
    bankaccount_number= models.CharField(max_length=64, default="Update Your Account", null=True, blank=True)
    home_address= models.CharField(max_length=64, default="Update Your Account", null=True, blank=True)
    email_address= models.CharField(max_length=64, default="Update Your Account", null=True, blank=True)
    phone_number= models.CharField(max_length=64, default="+234 ****", null=True, blank=True)
    pin_code= models.CharField(max_length=5, default="12345", null=True, blank=True)
    code= models.CharField(max_length=12, blank=True)
    recommended_by= models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name= "Reffered_by")
    balance= models.FloatField(default=0.0, null=True, blank=True)
    profile_picture= models.ImageField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.email}-{self.code}'

    @property
    def profile_pictureUrl(self):
        try:
            url= self.profile_picture.url
        except:
            url=''
        return url


    def get_recommended_profiles(self):
        query= Client.objects.all()
        my_recs= []
        for i in query:
            if i.recommended_by == self.user:
                my_recs.append(i)
        return my_recs

    def save(self, *args, **kwargs):
        if self.code == '':
            code= generate_ref_code()
            self.code= code
        super().save(*args, **kwargs)


class Wallet(models.Model):
    coin_type= models.CharField(max_length=20, null=True, blank=True)
    wallet_address= models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.coin_type}-{self.wallet_address}-Edit only"


class Euro_deposit(models.Model):
    client= models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    account_name= models.CharField(max_length=200, null=True, blank=True)
    account_number= models.CharField(max_length=64, null=True, blank=True)
    bank_name= models.CharField(max_length= 205, null=True, blank=True)
    amount= models.FloatField(default=0, null=True, blank=True)
    status= models.CharField(max_length=20, choices=[
        ('completed', 'Completed'),
        ('incomplete', 'Incomplete'),
    ], default='incomplete')
    date_created= models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.client.user.username

class USD_deposit(models.Model):
    client= models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    account_name= models.CharField(max_length=200, null=True, blank=True)
    account_number= models.CharField(max_length=64, null=True, blank=True)
    bank_name= models.CharField(max_length= 205, null=True, blank=True)
    amount= models.FloatField(default=0, null=True, blank=True)
    status= models.CharField(max_length=20, choices=[
        ('completed', 'Completed'),
        ('incomplete', 'Incomplete'),
    ], default='incomplete')
    date_created= models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.client.user.username

class CFA_deposit(models.Model):
    client= models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    account_name= models.CharField(max_length=200, null=True, blank=True)
    account_number= models.CharField(max_length=64, null=True, blank=True)
    bank_name= models.CharField(max_length= 205, null=True, blank=True)
    amount= models.FloatField(default=0, null=True, blank=True)
    status= models.CharField(max_length=20, choices=[
        ('completed', 'Completed'),
        ('incomplete', 'Incomplete'),
    ], default='incomplete')
    date_created= models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.client.user.username

class Naira_deposit(models.Model):
    client= models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    account_name= models.CharField(max_length=200, null=True, blank=True)
    account_number= models.CharField(max_length=64, null=True, blank=True)
    bank_name= models.CharField(max_length= 205, null=True, blank=True)
    amount= models.FloatField(default=0, null=True, blank=True)
    status= models.CharField(max_length=20, choices=[
        ('completed', 'Completed'),
        ('incomplete', 'Incomplete'),
    ], default='incomplete')
    date_created= models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.client.user.username

class CryptoData(models.Model):
    symbol = models.CharField(max_length=10)
    price = models.FloatField()
    market_cap = models.FloatField()

    def __str__(self):
        return self.symbol

class PendingCoinPurchase(models.Model):
    client= models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    transaction_type= models.CharField(max_length=64, null=True, blank=True)
    crypto_to_purchase= models.CharField(max_length=20, null=True, blank=True)
    amount= models.FloatField(default=0, null=True)
    recieving_wallet_address= models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.client.email_address

class PendingCoinSale(models.Model):
    client= models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    usd_value= models.FloatField(null=True, blank=True, default='0.0')
    naira_value= models.FloatField(null=True, blank=True, default='0.0')
    coin_type= models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.client.email_address

class PendingGiftCardSale(models.Model):
    client= models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    giftcard_type= models.CharField(max_length=20, null=True, blank=True, default='No Found')
    giftcard_amount= models.FloatField(null=True, blank=True, default='0.0')
    giftcard_number= models.CharField(max_length=100, null=True, blank=True, default='No number')
    country= models.CharField(max_length=30, null=True, blank=True, default='United States')
    amount= models.FloatField(null=True, blank=True, default='0.0')
    front_pic= models.ImageField(null=True, blank=True)
    back_pic= models.ImageField(null=True, blank=True)

    @property
    def front_picUrl(self):
        try:
            url= self.front_pic.url
        except:
            url=''
        return url

    @property
    def back_picUrl(self):
        try:
            url= self.back_pic.url
        except:
            url=''
        return url

    def __str__(self):
        return self.client.email_address

class Transaction(models.Model):
    client= models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    transaction_type= models.CharField(max_length=64, null=True, blank=True, default='Not Found')
    transaction_category= models.CharField(max_length=64, null=True, blank=True, choices=[
        ('Airtime', 'Airtime'),
        ('Data', 'Data'),
        ('CryptoPurchase', 'CryptoPurchase'),
        ('CryptoSale', 'CryptoSale'),
        ('Electricity', 'Electricity'),
        ('BetTopup', 'BetTopup'),
        ('GiftcardPurchase', 'GiftcardPurchase'),
        ('GiftcardSale', 'GiftcardSale'),
        ('CableTv', 'CableTv'),
        ('Withdrawal', 'Withdrawal'),
        ('Pluto Transfer', 'Pluto Transfer'),
    ])
    transaction_id= models.CharField(max_length=64, null=True, blank=True, default='Not Found')
    amount= models.FloatField(default=0, null=True)
    status= models.CharField(max_length=64, null=True, blank=True, choices=[
        ('completed', 'completed'),
        ('incomplete', 'incomplete'),
        ('pending', 'pending'),
        ('failed', 'failed'),
    ])
    created= models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.client.email_address

class cryptoTransactionHash(models.Model):
    client= models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    address_sent_to= models.CharField(max_length=200, null=True, blank=True, default='Not Found')
    amount= models.FloatField(default=0, null=True)
    crypto_sent= models.CharField(max_length=60, null=True, blank=True, default='Not Found')
    transaction_hash= models.CharField(max_length=500, null=True, blank=True, default='Not Found')
    created= models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.transaction_hash

class Account(models.Model):
    account_name= models.CharField(max_length=200, null=True, blank=True)
    account_number= models.CharField(max_length=64, null=True, blank=True)
    currency= models.CharField(max_length= 5, null=True, blank=True)
    bank_name= models.CharField(max_length= 205, null=True, blank=True)

    def __str__(self):
        return self.bank_name

class Withdrawal_request(models.Model):
    client= models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    client_email= models.CharField(max_length=200, null=True, blank=True)
    transaction_type= models.CharField(max_length=64, null=True, default='Withdrawal' )
    bank_name= models.CharField(max_length=100, null=True)
    bankaccount_number= models.CharField(max_length=100, null=True)
    amount= models.FloatField(default=0, null=True)

    def __str__(self):
        return self.client_email

class Minimum_withdrawal(models.Model):
    minimum_withdrawal= models.FloatField(default=0)

    def __str__(self):
        return f"Your minimum withdrawal goes here"

class Maximum_withdrawal(models.Model):
    maximum_withdrawal= models.FloatField(default=0)

    def __str__(self):
        return f"Your maximum withdrawal goes here"

class Giftcard(models.Model):
    card_type= models.CharField(max_length=30, null=True, blank=True)
    naira_rate= models.FloatField(default=500, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['card_type'], name='card_type')
        ]


    def __str__(self):
        return self.card_type

class Giftcard_buyrate(models.Model):
    sell_card_type= models.CharField(max_length=30, null=True, blank=True)
    naira_rate= models.FloatField(default=500, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sell_card_type'], name='sell_card_type')
        ]


    def __str__(self):
        return self.sell_card_type

class Crypto(models.Model):
    coin_type= models.CharField(max_length=30, null=True, blank=True)
    naira_rate= models.FloatField(default=1500, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['coin_type'], name='coin_type')
        ]


    def __str__(self):
        return self.coin_type

class SellCrypto(models.Model):
    sell_coin_type= models.CharField(max_length=30, null=True, blank=True)
    naira_rate= models.FloatField(default=1500, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sell_coin_type'], name='sell_coin_type')
        ]


    def __str__(self):
        return self.sell_coin_type

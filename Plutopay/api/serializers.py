from rest_framework import serializers
from .models import *
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

CustomUser = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        '''
        # Send registration email
        send_mail(
            'Welcome to Our Platform',
            'Thank you for registering with us.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        '''
        return user
'''
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid login credentials")
'''

class ClientAccountDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model= Client
        fields= ["id", "email_address", "first_name", "balance", "profile_picture", "pin_code"]


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model= Client
        fields= '__all__'

class ClientAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model= Client
        exclude= ["id", "user", "email_address", "balance", "code", "recommended_by"]

class ClientTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model= Transaction
        fields= '__all__'
        '''
        fields= ["id", "transaction_type", "amount", "status", "created"]
        '''

class CryptoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoData
        fields = ['symbol', 'price', 'market_cap']

class PendingCoinPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingCoinPurchase
        fields = '__all__'

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

class UsdSerializer(serializers.ModelSerializer):
    class Meta:
        model= USD_deposit
        fields= '__all__'

class EuroSerializer(serializers.ModelSerializer):
    class Meta:
        model= Euro_deposit
        fields= '__all__'

class CfaSerializer(serializers.ModelSerializer):
    class Meta:
        model= CFA_deposit
        fields= '__all__'

class NairaSerializer(serializers.ModelSerializer):
    class Meta:
        model= Naira_deposit
        fields= '__all__'

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model= Withdrawal_request
        fields= '__all__'

class GiftcardSerializer(serializers.ModelSerializer):
    class Meta:
        model= Giftcard
        fields= ['naira_rate']

class Giftcard_buyrateSerializer(serializers.ModelSerializer):
    class Meta:
        model= Giftcard_buyrate
        fields= ['naira_rate']

class Crypto_Serializer(serializers.ModelSerializer):
    class Meta:
        model= Crypto
        fields= ['naira_rate']

class SellCrypto_serializer(serializers.ModelSerializer):
    class Meta:
        model= Crypto
        fields= ['naira_rate']

class Wallet_addr_serializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields= '__all__'

class ClientAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ['code', 'pin_code']

class ClientAdminWithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal_request
        fields = '__all__'

class PendingBuyCryptoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class PendingSellCryptoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingCoinSale
        fields = '__all__'

class PendingBuyGiftcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields= '__all__'

class PendingSellGiftcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingGiftCardSale
        fields = '__all__'
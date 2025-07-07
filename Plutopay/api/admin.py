from django.contrib import admin

from .models import *


# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Client)
admin.site.register(Transaction)
admin.site.register(Crypto)
admin.site.register(SellCrypto)
admin.site.register(Withdrawal_request)
admin.site.register(Minimum_withdrawal)
admin.site.register(Maximum_withdrawal)
admin.site.register(cryptoTransactionHash)
admin.site.register(Giftcard)
admin.site.register(Giftcard_buyrate)
admin.site.register(PendingGiftCardSale)
admin.site.register(PendingCoinSale)

admin.site.register(Wallet)

from django.shortcuts import render

from django.http import JsonResponse

from rest_framework.response import Response

from .serializers import *

from .requestID import *

from rest_framework import status

from rest_framework.decorators import api_view, permission_classes

from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate

from django.core.exceptions import ObjectDoesNotExist

from django.core import mail

from django.template.loader import render_to_string

from django.utils.html import strip_tags

from django.conf import settings

from django.contrib.auth import update_session_auth_hash

import datetime
import json
import requests
import uuid
import os
import math

from django.contrib.auth import get_user_model
User = get_user_model()
# Create your views here.

@api_view(['Get'])
def overview(request):
    return Response({'message': 'welcome'})

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    if request.method == 'POST':
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = None
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
            except ObjectDoesNotExist:
                pass

        if not user:
            user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            subject = 'Login Notification'
            html_message = render_to_string('api/loginAlert.html', {'name':username})
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            to = user.email
            #mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'message': 'Login Form'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit_view(request):
    client= request.user.client
    if request.method == 'POST':
        prefered_currency= request.data.get('currencytype')
        amount= request.data.get('amount')
        if prefered_currency and amount:
            account_info= Account.objects.get(currency=prefered_currency)
            if account_info and prefered_currency == 'CFA':
                CFA_deposit.objects.create(
                    client= client,
                    amount= amount,
                    account_name= account_info.account_name,
                    account_number= account_info.account_number,
                    bank_name= account_info.bank_name
                )
                return Response({'message':'CFA deposit request made'}, status=status.HTTP_200_OK)
            if account_info and prefered_currency == 'USD':
                USD_deposit.objects.create(
                    client= client,
                    amount= amount,
                    account_name= account_info.account_name,
                    account_number= account_info.account_number,
                    bank_name= account_info.bank_name
                )
                return Response({'message':'USD deposit request made'}, status=status.HTTP_200_OK)
            if account_info and prefered_currency == 'EUR':
                Euro_deposit.objects.create(
                    client= client,
                    amount= amount,
                    account_name= account_info.account_name,
                    account_number= account_info.account_number,
                    bank_name= account_info.bank_name
                )
                return Response({'message':'EUR deposit request made'}, status=status.HTTP_200_OK)
            if account_info and prefered_currency == 'Naira':
                Naira_deposit.objects.create(
                    client= client,
                    amount= amount,
                    account_name= account_info.account_name,
                    account_number= account_info.account_number,
                    bank_name= account_info.bank_name
                )
                return Response({'message':'Naira deposit request made'}, status=status.HTTP_200_OK)
            else:
                Response({'message':'currency not available'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'message':'Invald amount and currency'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'message':'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'No credentials Sent'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit_view_activation(request):
    client= request.user.client
    if request.method == 'POST':
        prefered_currency= request.data.get('currencytype')
        if prefered_currency == 'Naira':
            payment_request= Naira_deposit.objects.filter(client=client)
            last_payment_request= payment_request.last()
            print(last_payment_request)
            print(last_payment_request.bank_name)
            serializer= NairaSerializer(last_payment_request, many=False)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Cannot Handle Request At This Time. Try Again Later'}, status=status.HTTP_400_BAD_REQUEST)

        if prefered_currency == 'CFA':
            payment_request= CFA_deposit.objects.filter(client=client)
            last_payment_request= payment_request.last()
            print(last_payment_request)
            print(last_payment_request.bank_name)
            serializer= CfaSerializer(last_payment_request, many=False)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Cannot Handle Request At This Time. Try Again Later'}, status=status.HTTP_400_BAD_REQUEST)

        if prefered_currency == 'USD':
            payment_request= USD_deposit.objects.filter(client=client)
            last_payment_request= payment_request.last()
            print(last_payment_request)
            print(last_payment_request.bank_name)
            serializer= UsdSerializer(last_payment_request, many=False)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Cannot Handle Request At This Time. Try Again Later'}, status=status.HTTP_400_BAD_REQUEST)

        if prefered_currency == 'EUR':
            payment_request= Euro_deposit.objects.filter(client=client)
            last_payment_request= payment_request.last()
            print(last_payment_request)
            print(last_payment_request.bank_name)
            serializer= EuroSerializer(last_payment_request, many=False)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Cannot Handle Request At This Time. Try Again Later'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'message': 'Currency not found. Try Again Later'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Only Post call is allowed'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit_view_activation_complete(request, pk):
    client= request.user.client
    if request.method == 'POST':
        prefered_currency= request.data.get('currencytype')
        activation_key= request.data.get('activationkey')
        if activation_key == 'ok' and prefered_currency == 'Naira':
            payment_details= Naira_deposit.objects.get(id=pk)
            update_payment_details= {'status': 'completed'}
            if payment_details:
                serializer= NairaSerializer(payment_details, data=update_payment_details, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    #Send email to user and admin notifying about deposit
                    return Response({'message': 'Naira Transfer Completed'}, status.HTTP_200_OK)
                else:
                    return Response({'message': 'Cannot Handle Request At This Time. Try Again Later'}, status=status.HTTP_400_BAD_REQUEST)

        if activation_key == 'ok' and prefered_currency == 'CFA':
            payment_details= CFA_deposit.objects.get(id=pk)
            update_payment_details= {'status': 'completed'}
            if payment_details:
                serializer= CfaSerializer(payment_details, data=update_payment_details, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    #Send email to user and admin notifying about deposit
                    return Response({'message': 'CFA Transfer Completed'}, status.HTTP_200_OK)
                else:
                    return Response({'message': 'Cannot Handle Request At This Time. Try Again Later'}, status=status.HTTP_400_BAD_REQUEST)

        if activation_key == 'ok' and prefered_currency == 'USD':
            payment_details= USD_deposit.objects.get(id=pk)
            update_payment_details= {'status': 'completed'}
            if payment_details:
                serializer= UsdSerializer(payment_details, data=update_payment_details, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    #Send email to user and admin notifying about deposit
                    return Response({'message': 'USD Transfer Completed'}, status.HTTP_200_OK)
                else:
                    return Response({'message': 'Cannot Handle Request At This Time. Try Again Later'}, status=status.HTTP_400_BAD_REQUEST)

        if activation_key == 'ok' and prefered_currency == 'EUR':
            payment_details= Euro_deposit.objects.get(id=pk)
            update_payment_details= {'status': 'completed'}
            if payment_details:
                serializer= EuroSerializer(payment_details, data=update_payment_details, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    #Send email to user and admin notifying about deposit
                    return Response({'message': 'Euro Transfer Completed'}, status.HTTP_200_OK)
                else:
                    return Response({'message': 'Cannot Handle Request At This Time. Try Again Later'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'message': 'Something went wrong. Try Again Later'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Only Post call is allowed'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def sell_crypto(request):
    client= request.user.client
    if request.method == 'GET':
        try:
            crypto_to_sell= request.query_params['coin']
            coin_rate= SellCrypto.objects.get(sell_coin_type=crypto_to_sell)
            print(coin_rate)
            if coin_rate:
                serializer= SellCrypto_serializer(coin_rate, many=False)
                print(coin_rate.naira_rate)
                if serializer:
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid Serializer'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Unable to get Crypto rate'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Message': 'Get Request'}, status=status.HTTP_200_OK)
    if request.method == 'POST':
        client_id= request.user.id
        client_info= Client.objects.get(user=client_id)
        crypto_to_sell= request.data.get('coin')
        amount= request.data.get('amount')
        naira_value= request.data.get('naira_value')
        order_id= 'PLUTOPAY Coin SALE'
        order_description="This is a coin Sale"
        price_currency= "USD"
        if amount and price_currency:
            wallet_addr= Wallet.objects.get(coin_type=crypto_to_sell)
            print(wallet_addr)
            if wallet_addr:
                serializer= Wallet_addr_serializer(wallet_addr, many=False)
                if serializer:
                    try:
                        PendingCoinSale.objects.create(
                            client= client,
                            usd_value= amount,
                            naira_value = naira_value,
                            coin_type= crypto_to_sell,
                        )
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    except:
                        return Response({'error':'error creating request'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': "Error processing request"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'You cannot sell this crypto at the moment. Please try again later!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': "Error processing request"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Post call is working fine'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Only Post call is allowed'}, status=status.HTTP_400_BAD_REQUEST)



'''
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def sell_crypto(request):
    if request.method == 'GET':
        try:
            crypto_to_sell= request.query_params['coin']
            coin_rate= SellCrypto.objects.get(sell_coin_type=crypto_to_sell)
            print(coin_rate)
            if coin_rate:
                serializer= SellCrypto_serializer(coin_rate, many=False)
                print(coin_rate.naira_rate)
                if serializer:
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid Serializer'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Unable to get Crypto rate'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Message': 'Get Request'}, status=status.HTTP_200_OK)
    if request.method == 'POST':
        client_id= request.user.id
        client_info= Client.objects.get(user=client_id)
        crypto_to_sell= request.data.get('coin')
        amount= request.data.get('amount')
        order_id= 'PLUTOPAY Coin SALE'
        order_description="This is a coin purchase"
        price_currency= "USD"
        if amount and price_currency:
            url= "https://api.nowpayments.io/v1/payment"
            payload= json.dumps({
                "price_amount": amount,
                "price_currency": price_currency,
                "pay_currency": crypto_to_sell,
                "order_id":  order_id,
                "order_description": order_description,
                "ipn_callback_url": 'https://nowpayments.io',
                "success_url": 'https://nowpayments.io',
                "cancel_url": 'https://nowpayments.io',
            })
            headers= {'x-api-key': 'VYCXGZC-7KAMM5Y-G3BD4AY-YEJ8MFY', 'Content-Type': 'application/json'}
            response= requests.request('POST', url, headers=headers, data=payload)
            res= response.json()
            print(res)
            try:
                PendingCoinSale.objects.create(
                    client= client,
                    coin_amount= amount,
                    coin_type= crypto_to_sell,
                )
            except:
                return Response({'error':'error creating request'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': res }, status=status.HTTP_200_OK)
        else:
            return Response({'error': "Error processing request"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Post call is working fine'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Only Post call is allowed'}, status=status.HTTP_400_BAD_REQUEST)
'''


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sell_crypto_status(request):
    if request.method == 'POST':
        client_id= request.user.id
        client_info= Client.objects.get(user=client_id)
        payment_id= request.data.get('paymentID')
        if payment_id:
            url= f"https://api.nowpayments.io/v1/payment/{payment_id}"
            payload= {}
            headers= {'x-api-key': 'VYCXGZC-7KAMM5Y-G3BD4AY-YEJ8MFY'}
            response = requests.request("GET", url, headers=headers, data=payload)
            res= response.json()
            print(res)
            return Response({'message': res}, status= status.HTTP_200_OK)
        else:
            return Response({'error': 'Error getting Payment ID'}, status= status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def sell_giftCard(request):
    client= request.user.client
    if request.method == 'GET':
        try:
            giftcard_to_sell= request.query_params['card']
            card_rate= Giftcard_buyrate.objects.get(sell_card_type=giftcard_to_sell)
            if card_rate:
                serializer= Giftcard_buyrateSerializer(card_rate, many=False)
                print(card_rate.naira_rate)
                if serializer:
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid Serializer'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Unable to get giftcard rate'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        card_type= request.data.get('cardtype')
        card_number= request.data.get('cardnumber')
        amount= request.data.get('amount')
        giftcard_Amount= request.data.get('giftcard_Amount')
        giftcard_front_pic= request.data.get('frontImage')
        giftcard_back_pic= request.data.get('backImage')
        if card_type and card_number and amount:
            client_id= request.user.id
            client_info= Client.objects.get(user=client_id)
            print(client_info.balance)
            if float(giftcard_Amount) < float(24):
                print('Your transaction has to be more than or equal to 50 USD')
                return Response({'error': 'Your transaction has to be more than or equal to 50 USD'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            elif float(giftcard_Amount) > float(24):
                print('Please Proceed with the transaction')
                try:
                    PendingGiftCardSale.objects.create(
                        client= client,
                        giftcard_type=card_type,
                        giftcard_amount=giftcard_Amount,
                        giftcard_number= card_number,
                        country= 'United States',
                        amount= amount,
                        front_pic= giftcard_front_pic,
                        back_pic= giftcard_back_pic
                    )
                except:
                    return Response({'error':'Cannot finish request!'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'message': 'Your sale has been logged, Please await processing.'}, status=status.HTTP_200_OK)
            else:
                print('Please deposit funds into your account to complete this transaction')
                return Response({'message': 'Please deposit funds into your account to complete this transaction'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'message': 'Working Fine'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def buy_giftCard(request):
    client= request.user.client
    request_id= generate_request_id()
    if request.method == 'GET':
        try:
            giftcard_to_purchase= request.query_params['card']
            card_rate= Giftcard.objects.get(card_type=giftcard_to_purchase)
            if card_rate:
                serializer= GiftcardSerializer(card_rate, many=False)
                print(card_rate.naira_rate)
                if serializer:
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid Serializer'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Unable to get giftcard rate'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        giftcard_to_purchase= request.data.get('card')
        amount= request.data.get('amount')
        recieving_email_address= request.user.email
        print(amount)
        if giftcard_to_purchase and amount and recieving_email_address:
            client_id= request.user.id
            client_info= Client.objects.get(user=client_id)
            print(client_info.balance)
            if float(client_info.balance) > float(0.0) and float(client_info.balance)  < float(amount) :
                print('You dont have sufficent balance to complete this transaction')
                return Response({'error': 'You dont have sufficent balance to complete this transaction'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif float(amount) < float(10000.00):
                print('Your transaction has to be more than or equal to 10,000 naira')
                return Response({'error': 'Your transaction has to be more than or equal to 10,000 naira'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            elif float(client_info.balance) > float(0.0) and float(client_info.balance)  >= float(amount) :
                print('You have sufficent balance to complete this transaction')
                client_current_balance= float(client_info.balance) - float(amount)
                client_update_data= {'balance': client_current_balance}
                serializer= ClientSerializer(client_info, data=client_update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    Transaction.objects.create(
                        client= client,
                        transaction_category='GiftcardPurchase',
                        transaction_type= f'GiftcardPurchase + {recieving_email_address}',
                        transaction_id= request_id,
                        amount= amount,
                        status= 'pending'
                    )
                    return Response({'message':'Transaction is processing'}, status=status.HTTP_200_OK)
                else:
                    print("Error:", response.json())
                    print(response.json())
                    Transaction.objects.create(
                        client= client,
                        transaction_category='GiftcardPurchase',
                        transaction_type= f'GiftcardPurchase + {recieving_email_address}',
                        transaction_id= request_id,
                        amount= amount,
                        status= 'failed'
                    )
                    return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_400_BAD_REQUEST)
            else:
                print('Please deposit funds into your account to complete this transaction')
                return Response({'message': 'Please deposit funds into your account to complete this transaction'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'message': 'Working Fine'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'error': 'Only post call allowed'}, status= status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def buy_crypto(request):
    client= request.user.client
    request_id= generate_request_id()
    if request.method == 'GET':
        try:
            crypto_to_purchase= request.query_params['coin']
            coin_rate= Crypto.objects.get(coin_type=crypto_to_purchase)
            print(coin_rate)
            if coin_rate:
                serializer= Crypto_Serializer(coin_rate, many=False)
                print(coin_rate.naira_rate)
                if serializer:
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid Serializer'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Unable to get Crypto rate'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Message': 'Get Request'}, status=status.HTTP_200_OK)
    if request.method == 'POST':
        crypto_to_purchase= request.data.get('coin')
        usd_amount= request.data.get('usd_amount')
        amount= request.data.get('amount')
        recieving_wallet_address= request.data.get('walletAddr')
        print(amount)
        if crypto_to_purchase and amount and recieving_wallet_address:
            client_id= request.user.id
            client_info= Client.objects.get(user=client_id)
            print(client_info.balance)
            if float(client_info.balance) > float(0.0) and float(client_info.balance)  < float(amount) :
                print('You dont have sufficent balance to complete this transaction')
                return Response({'error': 'You dont have sufficent balance to complete this transaction'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif float(amount) < float(15000.00):
                print('Your transaction has to be more than or equal to 10,000 naira')
                return Response({'error': 'Your transaction has to be more than or equal to 10,000 naira'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            elif float(client_info.balance) > float(0.0) and float(client_info.balance)  >= float(amount) :
                print('You have sufficent balance to complete this transaction')
                client_current_balance= float(client_info.balance) - float(amount)
                client_update_data= {'balance': client_current_balance}
                serializer= ClientSerializer(client_info, data=client_update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    Transaction.objects.create(
                        client= client,
                        transaction_category='CryptoPurchase',
                        transaction_type= f'CryptoPurchase + {recieving_wallet_address}',
                        transaction_id= request_id,
                        amount= amount,
                        status= 'pending'
                    )
                    return Response({'message':'Transaction is processing'}, status=status.HTTP_200_OK)
                else:
                    print("Error:", response.json())
                    print(response.json())
                    Transaction.objects.create(
                        client= client,
                        transaction_category='CryptoPurchase',
                        transaction_type= f'CryptoPurchase + {recieving_wallet_address}',
                        transaction_id= request_id,
                        amount= amount,
                        status= 'failed'
                    )
                    return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_400_BAD_REQUEST)
            else:
                print('Please deposit funds into your account to complete this transaction')
                return Response({'message': 'Please deposit funds into your account to complete this transaction'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            #return Response({'message': 'Working Fine'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'Message': 'POST Request'}, status=status.HTTP_200_OK)
    return Response({'Message': 'Buy Crypto'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            subject = 'Logout Notification'
            html_message = render_to_string('api/logoutMail.html', {'name':username})
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            to = user.email
            mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    if request.method == 'POST':
        client_id= request.user.id
        client_pk= request.user.client
        client_info= Client.objects.filter(user=client_id)
        last_three = Transaction.objects.filter(client=client_pk).order_by('-created')[:3]
        serializer= ClientAccountDashboardSerializer(client_info, many=True)
        transaction_serializer = ClientTransactionSerializer(last_three, many=True)
        return Response({'client_info':serializer.data, 'recent_transactions': transaction_serializer.data}, status= status.HTTP_200_OK)
    else:
        return Response({'message': 'Something went wrong'}, status= status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_transaction(request):
    if request.method == 'POST':
        client_id= request.user.client
        client_transactions= Transaction.objects.filter(client=client_id).order_by('-created')
        serializer= ClientTransactionSerializer(client_transactions, many=True)
        return Response(serializer.data, status= status.HTTP_200_OK)
    else:
        return Response({'message': 'Something went wrong'}, status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_settings(request):
    if request.method == 'POST':
        client= request.user.id
        client_info= Client.objects.get(user=client)
        serializer= ClientAccountSerializer(instance=client_info, data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status= status.HTTP_200_OK)
    else:
        return Response({'message': 'Something went wrong'}, status= status.HTTP_400_BAD_REQUEST)

'''
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def crypto_data_view(request):
    # Replace YOUR_API_KEY with your actual CryptoCompare API key
    api_key = '2dcbfb65ac46854c81507e5145075aac82d1b2631c5f105f2f80f387eefbb5e8'

    # Get a list of symbols from the query parameters, default to BTC, ETH, and XRP
    symbols = request.GET.getlist('symbols', ['BTC', 'ETH', 'Trx', 'BCH', 'USDT', 'USDC', ])
    symbols_str = ','.join(symbols)

    url = f'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbols_str}&tsyms=USD&api_key={api_key}'

    #url = f'https://min-api.cryptocompare.com/data/pricemultifull?fsyms=BTC,ETH,XRP&tsyms=USD&api_key={api_key}'

    try:
        response = requests.get(url)
        data = response.json()['RAW']

        crypto_data_list = []
        for symbol, info in data.items():
            crypto_data_list.append({
                'symbol': symbol,
                'price': info['USD']['PRICE'],
                'market_cap': info['USD']['MKTCAP']
            })

        serializer = CryptoDataSerializer(data=crypto_data_list, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cable_tv(request):
    client= request.user.client
    client_id= request.user.client.id
    user_id= request.user.id
    client_username= request.user.username
    client_email= request.user.email
    client_bal= request.user.client.balance
    client_info= Client.objects.get(user=user_id)
    #serviceID= request.data.get('serviceID')
    #billersCode= request.data.get('smartcardNumber')
    if request.method == 'GET':
        #GET VARIATION CODES
        serviceID= request.query_params['serviceID']
        if serviceID:
            url = f"https://sandbox.vtpass.com/api/service-variations?serviceID={serviceID}"
            response= requests.request('GET', url)
            print(response.json())
            res= response.json()
            try:
                if res['response_description'] == '000':
                    return Response(res, status=status.HTTP_200_OK)
            except:
                return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'Enter a cable Tv'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        #VERIFY SMARTCARD NUMBER AND PASS DATA INTO RESPONSE
        serviceID= request.data.get('serviceID')
        billersCode= request.data.get('smartcardNumber')
        if serviceID and billersCode:
            url = 'https://sandbox.vtpass.com/api/merchant-verify'
            payload= json.dumps({
                "serviceID": serviceID,
                "billersCode": billersCode,
            })
            username= 'bigtchub@gmail.com'
            password= 'derico12345'
            #headers = get_basic_auth_header(username, password)
            headers={'api-key': 'e92c761975af7a8ba37f1cbb6698ffd2','secret-key':'SK_849b33829800f30862b2c899ef9c887c17f24aabb4e', 'Content-Type': 'application/json'}
            response = requests.request('POST', url, headers=headers, data=payload)
            print(response.json())
            res= response.json()
            try:
                if res:
                    return Response(res, status=status.HTTP_200_OK)
            except:
                return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'Invalid information'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'cable_tv'}, status= status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def buy_cable_tv(request):
    client= request.user.client
    client_id= request.user.client.id
    user_id= request.user.id
    client_username= request.user.username
    client_email= request.user.email
    client_bal= request.user.client.balance
    client_info= Client.objects.get(user=user_id)
    request_id= generate_request_id()
    serviceID= request.data.get('serviceID')
    billersCode= request.data.get('smartcardNumber')
    variation_code= request.data.get('variationCode')
    quantity= request.data.get('quantity')
    variation_amount= request.data.get('variationAmount')
    amount= (int(math.ceil(float(variation_amount) / 10.0)) * 10) * int(quantity)
    variationAmount= float(variation_amount) * float(quantity)
    phone= request.user.client.phone_number
    subscription_type= 'change'
    print(serviceID, billersCode, variation_code, quantity, variation_amount)
    if request.method == 'POST':
        if amount and float(client_bal) > float(amount):
            if request_id and serviceID and billersCode and variation_code and amount and phone and subscription_type and quantity :
                url= "https://sandbox.vtpass.com/api/pay"
                payload= json.dumps({
                    "request_id": request_id,
                    "serviceID": serviceID,
                    "billersCode": billersCode,
                    "variation_code": variation_code,
                    "amount": variationAmount,
                    "phone":phone,
                    "subscription_type":subscription_type,
                    "quantity": quantity
                })
                headers={'api-key': 'e92c761975af7a8ba37f1cbb6698ffd2','secret-key':'SK_849b33829800f30862b2c899ef9c887c17f24aabb4e', 'Content-Type': 'application/json'}
                response= requests.request('POST', url, headers=headers, data=payload)
                print(response.json())
                res= response.json()
                description = res.get('response_description', '').strip()
                print(description)
                if description == 'TRANSACTION SUCCESSFUL':
                    client_current_balance= float(client_info.balance) - float(amount)
                    client_update_data= {'balance': client_current_balance}
                    serializer= ClientSerializer(client_info, data=client_update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        Transaction.objects.create(
                            client= client,
                            transaction_category='CableTv',
                            transaction_type= f'CableTv + {serviceID}',
                            transaction_id= request_id,
                            amount= amount,
                            status= 'completed'
                        )
                        return Response(res, status=status.HTTP_200_OK)
                    else:
                        Transaction.objects.create(
                            client= client,
                            transaction_category='CableTv',
                            transaction_type= f'CableTv + {serviceID}',
                            transaction_id= request_id,
                            amount= amount,
                            status= 'failed'
                        )
                        return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_400_BAD_REQUEST)
                else:
                    print('Error getting info')
                return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_401_UNAUTHORIZED)

    return Response({'message': 'cable_tv'}, status= status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def renew_cable_tv(request):
    client= request.user.client
    client_id= request.user.client.id
    user_id= request.user.id
    client_username= request.user.username
    client_email= request.user.email
    client_bal= request.user.client.balance
    client_info= Client.objects.get(user=user_id)
    request_id= generate_request_id()
    serviceID= request.data.get('serviceID')
    billersCode= request.data.get('smartcardNumber')
    variation_code= request.data.get('variationCode')
    variation_amount= request.data.get('variationAmount')
    print(variation_amount)
    amount= int(math.ceil(float(variation_amount) / 10.0)) * 10
    print(amount)
    variationAmount= float(variation_amount)
    print(variationAmount)
    phone= request.data.get('phone')
    subscription_type= 'renew'
    if request.method == 'POST':
        if amount and float(client_bal) < float(amount):
            if request_id and serviceID and billersCode and variation_code and amount and phone and subscription_type:
                url= "https://sandbox.vtpass.com/api/pay"
                payload= json.dumps({
                    "request_id": request_id,
                    "serviceID": serviceID,
                    "billersCode": billersCode,
                    "amount": variationAmount,
                    "phone":phone,
                    "subscription_type":subscription_type,
                })
                headers={'api-key': 'e92c761975af7a8ba37f1cbb6698ffd2','secret-key':'SK_849b33829800f30862b2c899ef9c887c17f24aabb4e', 'Content-Type': 'application/json'}
                response= requests.request('POST', url, headers=headers, data=payload)
                print(response.json())
                #Process Purchase
                return Response({'message': response.json()}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_401_UNAUTHORIZED)
    return Response({'message': 'cable_tv'}, status= status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_gambler(request):
    client= request.user.client
    client_id= request.user.client.id
    user_id= request.user.id
    client_username= request.user.username
    client_email= request.user.email
    client_bal= request.user.client.balance
    client_info= Client.objects.get(user=user_id)
    if request.method == 'GET':
        #Verify Gampbler
        provider= request.query_params['provider']
        customerId= request.query_params['customerId']
        url = f"https://www.nellobytesystems.com/APIVerifyBettingV1.asp?UserID=CK101129504&APIKey=C6W64FX0BH960Z3GW21KJ2458JA98522C0NHD69VUJJI75CVO1ML4E3GP75K97U0&BettingCompany={provider}&CustomerID={customerId}"
        try:
            response= requests.request('GET', url)
            print(response.json())
            res= response.json()
            if res['status'] == '00':
                return Response(res, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message':'Verify Gambler'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bet_topup(request):
    client= request.user.client
    client_id= request.user.client.id
    user_id= request.user.id
    client_username= request.user.username
    client_email= request.user.email
    client_bal= request.user.client.balance
    client_info= Client.objects.get(user=user_id)
    request_id= generate_request_id()
    if request.method == 'GET':
        BettingCompany= request.query_params['BettingCompany']
        CustomerID= request.query_params['CustomerID']
        Amount= request.query_params['Amount']
        total_amount= float(Amount) + float(110)
        if BettingCompany and CustomerID and Amount and float(Amount) > float(999):
            if float(client_bal) > float(total_amount):
                url = f'https://www.nellobytesystems.com/APIBettingV1.asp?UserID=CK101129504&APIKey=C6W64FX0BH960Z3GW21KJ2458JA98522C0NHD69VUJJI75CVO1ML4E3GP75K97U0&BettingCompany={BettingCompany}&CustomerID={CustomerID}&Amount={Amount}&RequestID={request_id}'
                response= requests.request('GET', url)
                #process transaction
                res= response.json()
                status= res['status']
                print(res)
                if str(status) == '00':
                    client_current_balance= float(client_info.balance) - float(amount)
                    client_update_data= {'balance': client_current_balance}
                    serializer= ClientSerializer(client_info, data=client_update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        Transaction.objects.create(
                            client= client,
                            transaction_category='BetTopup',
                            transaction_type= f'{BettingCompany}',
                            transaction_id= request_id,
                            amount= total_amount,
                            status= 'completed'
                        )
                        return Response(res, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'You do not have sufficent balance to complete this transaction'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid Request'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Method not allowed'}, status= status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Bet Topup'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_meter(request):
    client= request.user.client
    client_id= request.user.client.id
    user_id= request.user.id
    client_username= request.user.username
    client_email= request.user.email
    client_bal= request.user.client.balance
    client_info= Client.objects.get(user=user_id)
    if request.method == 'POST':
        billersCode= int(request.data.get('billersCode'))
        serviceID= request.data.get('serviceID')
        meterType= request.data.get('meterType')
        if billersCode and serviceID and meterType:
            url = f"https://sandbox.vtpass.com/api/merchant-verify"
            payload= json.dumps({
                "billersCode": billersCode,
                "serviceID": serviceID,
                "type": meterType,
            })
            headers={'api-key': 'e92c761975af7a8ba37f1cbb6698ffd2','secret-key':'SK_849b33829800f30862b2c899ef9c887c17f24aabb4e', 'Content-Type': 'application/json'}
            response= requests.request('POST', url, headers=headers, data=payload)
            print(response.json())
            res= response.json()
            return Response(res, status=status.HTTP_200_OK)
        else:
            return Response({'error':'Invalid Request'}, status= status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Bad Request'}, status= status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Verify Meter'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_electricity(request):
    client= request.user.client
    client_id= request.user.client.id
    user_id= request.user.id
    client_username= request.user.username
    client_email= request.user.email
    client_bal= request.user.client.balance
    client_info= Client.objects.get(user=user_id)
    request_id= generate_request_id()
    if request.method == 'POST':
        billersCode= request.data.get('billersCode')
        serviceID= request.data.get('serviceID')
        variation_code= request.data.get('meterType')
        amount= request.data.get('amount')
        phone= request.data.get('phone')
        if request_id and billersCode and serviceID and variation_code and amount and phone:
            if variation_code == 'prepaid' and float(client_bal) > float(amount):
                url = 'https://sandbox.vtpass.com/api/pay'
                payload= json.dumps({
                    "request_id":request_id,
                    "serviceID":serviceID,
                    "billersCode":billersCode,
                    "variation_code":variation_code,
                    "amount":amount,
                    "phone":phone,
                })
                headers={'api-key': 'e92c761975af7a8ba37f1cbb6698ffd2','secret-key':'SK_849b33829800f30862b2c899ef9c887c17f24aabb4e', 'Content-Type': 'application/json'}
                response= requests.request('POST', url, headers=headers, data=payload)
                res= response.json()
                print(response.json())
                status_value= res['content']['transactions']['status']
                print(status_value)
                if str(status_value) != 'failed':
                    client_current_balance= float(client_info.balance) - float(amount)
                    client_update_data= {'balance': client_current_balance}
                    serializer= ClientSerializer(client_info, data=client_update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        Transaction.objects.create(
                            client= client,
                            transaction_category='Electricity',
                            transaction_type= f"Token- {res['token']}",
                            transaction_id= request_id,
                            amount= amount,
                            status= 'completed'
                        )
                        return Response(res, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_400_BAD_REQUEST)

            elif variation_code == 'postpaid' and float(client_bal) > float(amount):
                url = 'https://sandbox.vtpass.com/api/pay'
                payload= json.dumps({
                    "request_id":request_id,
                    "serviceID":serviceID,
                    "billersCode":billersCode,
                    "variation_code":variation_code,
                    "amount":amount,
                    "phone":phone,
                })
                headers={'api-key': 'e92c761975af7a8ba37f1cbb6698ffd2','secret-key':'SK_849b33829800f30862b2c899ef9c887c17f24aabb4e', 'Content-Type': 'application/json'}
                response= requests.request('POST', url, headers=headers, data=payload)
                res= response.json()
                print(res)
                status_value= res['content']['transactions']['status']
                print(status_value)
                if str(status_value) != 'failed':
                    client_current_balance= float(client_info.balance) - float(amount)
                    client_update_data= {'balance': client_current_balance}
                    serializer= ClientSerializer(client_info, data=client_update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        Transaction.objects.create(
                            client= client,
                            transaction_category='Electricity',
                            transaction_type= f'PostPaid',
                            transaction_id= request_id,
                            amount= amount,
                            status= 'completed'
                        )
                        return Response(res, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Service not found'}, status= status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid Request'}, status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Method not allowed'}, status= status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Buy Electricity'}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def buy_data(request):
    client= request.user.client
    client_id= request.user.client.id
    user_id= request.user.id
    client_username= request.user.username
    client_email= request.user.email
    client_bal= request.user.client.balance
    client_info= Client.objects.get(user=user_id)
    if request.method == 'GET':
        serviceID= request.query_params['serviceID']
        print(serviceID)
        if serviceID:
            url = f"https://sandbox.vtpass.com/api/service-variations?serviceID={serviceID}"
            response= requests.request('GET', url)
            print(response.json())
            res= response.json()
            try:
                if res['response_description'] == '000':
                    return Response( res, status=status.HTTP_200_OK)
            except:
                return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'Enter a valid network provider'}, status=status.HTTP_400_BAD_REQUEST)
    if request.method== 'POST':
        request_id= generate_request_id()
        serviceID= request.data.get('serviceID')
        billersCode= request.data.get('phone')
        phone= request.data.get('phone')
        variation_code= request.data.get('variation_code')
        variation_amount= request.data.get('variation_amount')
        amount= int(math.ceil(float(variation_amount) / 10.0)) * 10
        print(amount)
        if amount and float(client_bal) > float(amount):
            if request_id and serviceID and billersCode and variation_code and amount and phone :
                url= "https://sandbox.vtpass.com/api/pay"
                payload= json.dumps({
                    "request_id": request_id,
                    "serviceID": serviceID,
                    "billersCode": billersCode,
                    "variation_code": variation_code,
                    "phone":phone
                })
                headers={'api-key': 'e92c761975af7a8ba37f1cbb6698ffd2','secret-key':'SK_849b33829800f30862b2c899ef9c887c17f24aabb4e', 'Content-Type': 'application/json'}
                response= requests.request('POST', url, headers=headers, data=payload)
                print(response.json())
                res= response.json()
                #Process Purchase
                if res['code'] == '000':
                    client_current_balance= float(client_bal) - float(amount)
                    client_update_data= {'balance': client_current_balance}
                    serializer= ClientSerializer(client_info, data=client_update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        Transaction.objects.create(
                            client= client,
                            transaction_category='Data',
                            transaction_type= res['content']['transactions']['product_name'],
                            transaction_id= request_id,
                            amount= amount,
                            status= 'completed'
                        )
                        print('balance updated')
                    return Response(response.json(), status=status.HTTP_200_OK)
                else:
                    print("Error:", response.json())
                    print(response.json())
                    Transaction.objects.create(
                        client= client,
                        transaction_category='Data',
                        transaction_type= res['content']['transactions']['product_name'],
                        transaction_id= request_id,
                        amount= amount,
                        status= 'failed'
                    )
                    return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Failed Request, Try again later'}, status= status.HTTP_401_UNAUTHORIZED)
    return Response({'message': 'Buy Data'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_airtime(request):
    client= request.user.client
    client_id= request.user.client.id
    user_id= request.user.id
    client_username= request.user.username
    client_email= request.user.email
    client_bal= request.user.client.balance
    client_info= Client.objects.get(user=user_id)
    if request.method == 'POST':
        amount= request.data.get('amount')
        phone= request.data.get('phone')
        serviceID= request.data.get('serviceID')
        request_id= generate_request_id()
        if amount and phone and serviceID and request_id:
            if float(client_bal) > float(amount) and float(amount) >= float(100):
                #process transaction
                url = "https://sandbox.vtpass.com/api/pay"
                payload= json.dumps({
                    "request_id": request_id,
                    "serviceID": serviceID,
                    "phone": phone,
                    "amount": amount,
                })
                headers={'api-key': 'e92c761975af7a8ba37f1cbb6698ffd2','secret-key':'SK_849b33829800f30862b2c899ef9c887c17f24aabb4e', 'Content-Type': 'application/json'}
                response= requests.request('POST', url, headers=headers, data=payload)
                res= response.json()
                if res['code'] == '000':
                    print("Airtime purchased successfully")
                    print(response.json())
                    client_current_balance= float(client_bal) - float(amount)
                    client_update_data= {'balance': client_current_balance}
                    serializer= ClientSerializer(client_info, data=client_update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        Transaction.objects.create(
                            client= client,
                            transaction_category='Airtime',
                            transaction_type= res['content']['transactions']['product_name'],
                            transaction_id= request_id,
                            amount= amount,
                            status= 'completed'
                        )
                        return Response(response.json(), status=status.HTTP_200_OK)
                else:
                    Transaction.objects.create(
                        client= client,
                        transaction_category='Airtime',
                        transaction_type= res['content']['transactions']['product_name'],
                        transaction_id= request_id,
                        amount= amount,
                        status= 'failed'
                    )
                    return Response({'error':'Transaction failed'}, status= status.HTTP_400_BAD_REQUEST)
            elif float(amount) < float(100):
                #amount is less than #100
                return Response({'error', 'Amount is less than 100 naira'}, status= status.HTTP_400_BAD_REQUEST)
            elif float(amount) > float(client_bal):
                #amount is greater than balance
                return Response({'error', 'Amount is greater than balance'}, status= status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error', 'Invalid request'}, status= status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error', 'Missing parameter'}, status= status.HTTP_400_BAD_REQUEST)
    return Response({'message':'Buy Airtime'}, status= status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdrawal(request):
    client= request.user.client
    client_id= request.user.client.id
    user_id= request.user.id
    client_username= request.user.username
    client_email= request.user.email
    client_bal= request.user.client.balance
    client_info= Client.objects.get(user=user_id)
    bank_name= request.user.client.bank_name
    bankaccount_number= request.user.client.bankaccount_number
    minimum_withdrawal= Minimum_withdrawal.objects.all()
    maximum_withdrawal= Maximum_withdrawal.objects.all()
    for i in minimum_withdrawal:
        minimum_withdrawal_amount= i.minimum_withdrawal
    for i in maximum_withdrawal:
        maximum_withdrawal_amount= i.maximum_withdrawal
    if request.method == 'POST':
        amount= request.data.get('amount')
        if float(amount) > float(minimum_withdrawal_amount) and float(client_bal) > float(amount):
            if bank_name != '' and bankaccount_number !='':
                client_current_balance= float(client_bal) - float(amount)
                client_update_data= {'balance': client_current_balance}
                serializer= ClientSerializer(client_info, data=client_update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    Withdrawal_request.objects.create(
                        client= client,
                        client_email= client_email,
                        bank_name= bank_name,
                        bankaccount_number= bankaccount_number,
                        amount= amount
                    )
                    return Response({'message':'Withdrawal Complete'}, status= status.HTTP_200_OK)
            else:
                return Response({'message': 'Please go to your account settings and add a valid bank account detail'}, status=status.HTTP_401_UNAUTHORIZED)
        if float(amount) > float(maximum_withdrawal_amount) and float(client_bal) > float(amount):
            return Response({'message': 'Cannot complete this transaction'}, status=status.HTTP_400_BAD_REQUEST)
        if float(amount) < float(minimum_withdrawal_amount) and float(client_bal) > float(amount):
            return Response({'message': 'Cannot complete this transaction'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Cannot complete this transaction'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message':'Withdrawal View'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_transaction_hash(request):
    if request.method == 'POST':
        client= request.user.client
        client_email= request.user.email
        address_sent_to= request.data.get('payAddress')
        amount= request.data.get('payAmount')
        crypto_sent= request.data.get('network')
        transaction_hash= request.data.get('transactionHash')
        if transaction_hash != '' and float(amount) >= 25 :
            try:
                cryptoTransactionHash.objects.create(
                    client= client,
                    address_sent_to= address_sent_to,
                    amount= amount,
                    crypto_sent= crypto_sent,
                    transaction_hash= transaction_hash,
                    )
                return Response({'message': 'Transaction Hash Recorded'}, status=status.HTTP_200_OK)
            except:
                return Response({'message': 'Something went wrong, please contact support'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'message': 'Cannot complete this transaction'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer_funds(request):
    if request.method == 'POST':
        client= request.user.client
        user_id= request.user.id
        client_username= request.user.username
        client_pk= request.user.client.id
        client_balance= client.balance
        client_email= client.email_address
        account_id = request.data.get('account_id')
        destination_client_account= account_id.strip() if account_id else None
        amount= request.data.get('amount')
        if float(client_balance) > float(amount):
            try:
                destination_client_account_info= User.objects.get(username= destination_client_account)
                if destination_client_account_info.username != client_username:
                    print(destination_client_account_info.username)
                    print(destination_client_account_info.client.balance)
                    newClientbal= float(client_balance) - float(amount)
                    new_destination_client_account_bal = float(destination_client_account_info.client.balance) + float(amount)
                    client_info= Client.objects.get(user=user_id)
                    destination_client_account_info_query= Client.objects.filter(id=destination_client_account_info.client.id)
                    #Query to update sender
                    client_update_data= {'balance': newClientbal}
                    debit_serializer= ClientSerializer(client_info, data=client_update_data, partial=True)
                    #Add debit to transaction history
                    if debit_serializer.is_valid():
                        debit_serializer.save()
                        Transaction.objects.create(
                            client= client,
                            transaction_id = f"Transfer to {getattr(destination_client_account_info, 'username', 'Unknown')}",
                            transaction_type= 'Debit',
                            transaction_category= 'Pluto Transfer',
                            amount= amount,
                            status= 'completed'
                            )
                    #Query to update receiver
                    receiverClient_update_data= {'balance': new_destination_client_account_bal}
                    credit_serializer= ClientSerializer(destination_client_account_info.client, data=receiverClient_update_data, partial=True)
                    #Add credit to transaction history
                    if credit_serializer.is_valid():
                        credit_serializer.save()
                        Transaction.objects.create(
                            client= destination_client_account_info.client,
                            transaction_id = f"Transfer from {client_username}",
                            transaction_type= 'Credit',
                            transaction_category= 'Pluto Transfer',
                            amount= amount,
                            status= 'completed'
                        )
                    #Send credit email to receiver
                    '''
                    credit_subject = 'Credit Notification'
                    credit_html_message = render_to_string('api/creditMail.html', {'name':username})
                    credit_plain_message = strip_tags(credit_html_message)
                    from_email = settings.EMAIL_HOST_USER
                    credit_to = user.email
                    try:
                        mail.send_mail(credit_subject, credit_plain_message, from_email, [credit_to], html_message=credit_html_message)
                        return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
                    except Exception as e:
                        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    #Send Debit email to receiver
                    debit_subject = 'Debit Notification'
                    debit_html_message = render_to_string('api/debitMail.html', {'name':username})
                    debit_plain_message = strip_tags(debit_html_message)
                    from_email = settings.EMAIL_HOST_USER
                    debit_to = user.email
                    try:
                        mail.send_mail(debit_subject, plain_message, from_email, [debit_to], html_message=debit_html_message)
                        return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
                    except Exception as e:
                        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    '''
                    return Response({'message': 'Transfer Successful'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'This account is not allowed! Quit trying to transfer funds to yourself'}, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({'message': 'Account does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Sorry but you do not have sufficent account balance to carry out this transaction'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message':'Transfer funds View'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admindashboard(request):
    if request.method == 'POST':
        clients= Client.objects.all()
        serializer= ClientAdminSerializer(clients, many=True)
        return Response(serializer.data, status= status.HTTP_200_OK)
    else:
        return Response({'message': 'Something went wrong'}, status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def confirmwithdrawal(request):
    if request.method == 'POST':
        withdrawals= Withdrawal_request.objects.all()
        serializer= ClientAdminWithdrawalSerializer(withdrawals, many=True)
        return Response(serializer.data, status= status.HTTP_200_OK)
    else:
        return Response({'message': 'Request not allowed'}, status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def confirmBuyCrypto(request):
    if request.method == 'POST':
        purchase= Transaction.objects.filter(transaction_category='CryptoPurchase', status='pending')
        serializer= PendingBuyCryptoSerializer(purchase, many=True)
        return Response(serializer.data, status= status.HTTP_200_OK)
    else:
        return Response({'message': 'Request not allowed'}, status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def confirmSellCrypto(request):
    if request.method == 'POST':
        sale= PendingCoinSale.objects.all()
        serializer= PendingSellCryptoSerializer(sale, many=True)
        return Response(serializer.data, status= status.HTTP_200_OK)
    else:
        return Response({'message': 'Request not allowed'}, status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def confirmBuyGiftCard(request):
    if request.method == 'POST':
        purchase= Transaction.objects.filter(transaction_category='GiftcardPurchase', status='pending')
        serializer= PendingBuyGiftcardSerializer(purchase, many=True)
        return Response(serializer.data, status= status.HTTP_200_OK)
    else:
        return Response({'message': 'Request not allowed'}, status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def confirmSellGiftcard(request):
    if request.method == 'POST':
        sale= PendingGiftCardSale.objects.all()
        serializer= PendingSellGiftcardSerializer(sale, many=True)
        return Response(serializer.data, status= status.HTTP_200_OK)
    else:
        return Response({'message': 'Request not allowed'}, status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def updateBuyCrypto(request, pk):
    if request.method == 'POST':
        try:
            transaction= Transaction.objects.get(id=pk, transaction_category='CryptoPurchase', status='pending')
            if transaction:
                transaction_id= transaction.id
                transaction_amount= transaction.amount
                client_id= transaction.client.id
                client= Client.objects.get(id=client_id)
                client_email= client.email_address
                client_firstName= client.first_name
                '''
                subject= "Crypto Purchase Notification"
                html_message= render_to_string('api/cryptoPurchaseMail.html', {'name':client_firstName, 'amount':transaction_amount})
                plain_message= strip_tags(html_message)
                from_email= settings.EMAIL_HOST_USER
                '''
                new_transaction_status= 'completed'
                transaction_update_data= {'status': new_transaction_status}
                serializer= ClientTransactionSerializer(transaction, data=transaction_update_data, partial=True)
                '''
                try:
                    mail.send_mail(subject, plain_message, from_email, [client_email], html_message=html_message)
                    return Response({'message': 'Crypto Purchase Notification Sent'}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                '''
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'message':'Unable to process crypto purchase'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message':'Unable to get transaction'}, status= status.HTTP_400_BAD_REQUEST)
        except Transaction.DoesNotExist:
            return Response({'message': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message':'Method not allowed'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def declineBuyCrypto(request, pk):
    if request.method == 'POST':
        try:
            transaction= Transaction.objects.get(id=pk, transaction_category='CryptoPurchase', status='pending')
            if transaction:
                transaction_id= transaction.id
                transaction_amount= transaction.amount
                client_id= transaction.client.id
                client= Client.objects.get(id=client_id)
                client_email= client.email_address
                client_firstName= client.first_name
                client_balance= client.balance
                '''
                subject= "Crypto Purchase Failed"
                html_message= render_to_string('api/cryptoPurchaseMail.html', {'name':client_firstName, 'amount':transaction_amount})
                plain_message= strip_tags(html_message)
                from_email= settings.EMAIL_HOST_USER
                '''
                new_transaction_status= 'failed'
                transaction_update_data= {'status': new_transaction_status}
                client_new_balance= {'balance': float(client_balance) + float(transaction_amount)}
                serializer= ClientTransactionSerializer(transaction, data=transaction_update_data, partial=True)
                client_serializer= ClientSerializer(client, data=client_new_balance, partial=True)
                '''
                try:
                    mail.send_mail(subject, plain_message, from_email, [client_email], html_message=html_message)
                    return Response({'message': 'Crypto Purchase Notification Sent'}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                '''
                if serializer.is_valid() and client_serializer.is_valid():
                    serializer.save()
                    client_serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'message':'Unable to process crypto purchase'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message':'Unable to get transaction'}, status= status.HTTP_400_BAD_REQUEST)
        except Transaction.DoesNotExist:
            return Response({'message': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Method not allowed'}, status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def updateSellCrypto(request, pk):
    if request.method == 'POST':
        try:
            coin_sale= PendingCoinSale.objects.get(id=pk)
            if coin_sale:
                usd_value= coin_sale.usd_value
                naira_value= coin_sale.naira_value
                coin_type= coin_sale.coin_type
                client_id= coin_sale.client.id
                request_id= generate_request_id()
                if client_id:
                    try:
                        client_info= Client.objects.get(id=client_id)
                        if client_info:
                            new_client_bal= {'balance': float(naira_value) + float(client_info.balance)}
                            update_client_bal= ClientSerializer(client_info, data=new_client_bal, partial=True)
                            if update_client_bal.is_valid():
                                update_client_bal.save()
                                coin_sale.delete()
                                Transaction.objects.create(
                                    client= client_info,
                                    transaction_type= f'CryptoSale - ${usd_value} - ${coin_type}',
                                    transaction_category= 'CryptoSale',
                                    transaction_id= request_id,
                                    amount= naira_value,
                                    status= 'completed',
                                )
                                '''
                                subject= "Crypto Sale"
                                html_message= render_to_string('api/cryptoSaleMail.html', {'name':client_firstName})
                                plain_message= strip_tags(html_message)
                                from_email= settings.EMAIL_HOST_USER

                                try:
                                    mail.send_mail(subject, plain_message, from_email, [client_email], html_message=html_message)
                                    return Response({'message': 'Crypto Purchase Notification Sent'}, status=status.HTTP_200_OK)
                                except Exception as e:
                                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                                '''
                                return Response({'message':'Crypto sale updated'}, status=status.HTTP_200_OK)
                            else:
                                return Response({'message':'Error updating request'}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({'message':'unable to find client'}, status=status.HTTP_404_NOT_FOUND)
                    except Client.DoesNotExist:
                        return Response({'message':'Cannot find client associated with this transaction'}, status= status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'message':'Cannot information not found'}, status= status.HTTP_404_NOT_FOUND)
        except PendingCoinSale.DoesNotExist:
            return Response({'message':'Crypto sale transaction not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message':'Request not allowed'}, status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def declineSellCrypto(request, pk):
    if request.method == 'POST':
        try:
            coin_sale= PendingCoinSale.objects.get(id=pk)
            if coin_sale:
                usd_value= coin_sale.usd_value
                naira_value= coin_sale.naira_value
                coin_type= coin_sale.coin_type
                client_id= coin_sale.client.id
                request_id= generate_request_id()
                if client_id:
                    try:
                        client_info= Client.objects.get(id=client_id)
                        if client_info:
                            coin_sale.delete()
                            Transaction.objects.create(
                                client= client_info,
                                transaction_type= f'CryptoSale - ${usd_value} - ${coin_type}',
                                transaction_category= 'CryptoSale',
                                transaction_id= request_id,
                                amount= naira_value,
                                status= 'failed',
                            )
                            '''
                            subject= "Crypto Sale Declined"
                            html_message= render_to_string('api/cryptoSaleMail.html', {'name':client_firstName})
                            plain_message= strip_tags(html_message)
                            from_email= settings.EMAIL_HOST_USER

                            try:
                                mail.send_mail(subject, plain_message, from_email, [client_email], html_message=html_message)
                                return Response({'message': 'Crypto Purchase Notification Sent'}, status=status.HTTP_200_OK)
                            except Exception as e:
                                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                            '''
                            return Response({'message':'Crypto sale updated'}, status=status.HTTP_200_OK)
                        else:
                            return Response({'message':'unable to find client'}, status=status.HTTP_404_NOT_FOUND)
                    except Client.DoesNotExist:
                        return Response({'message':'Cannot find client associated with this transaction'}, status= status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'message':'Cannot information not found'}, status= status.HTTP_404_NOT_FOUND)
        except PendingCoinSale.DoesNotExist:
            return Response({'message':'Crypto sale transaction not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message':'Request not allowed'}, status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def updateBuyGiftcard(request, pk):
    if request.method == 'POST':
        try:
            transaction= Transaction.objects.get(id=pk, transaction_category='GiftcardPurchase', status='pending')
            if transaction:
                transaction_id= transaction.id
                transaction_amount= transaction.amount
                client_id= transaction.client.id
                client= Client.objects.get(id=client_id)
                client_email= client.email_address
                client_firstName= client.first_name
                '''
                subject= "Giftcard Purchase Notification"
                html_message= render_to_string('api/GiftcardPurchaseMail.html', {'name':client_firstName, 'amount':transaction_amount})
                plain_message= strip_tags(html_message)
                from_email= settings.EMAIL_HOST_USER
                '''
                new_transaction_status= 'completed'
                transaction_update_data= {'status': new_transaction_status}
                serializer= ClientTransactionSerializer(transaction, data=transaction_update_data, partial=True)
                '''
                try:
                    mail.send_mail(subject, plain_message, from_email, [client_email], html_message=html_message)
                    return Response({'message': 'Giftcard Purchase Notification Sent'}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                '''
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'message':'Unable to process Giftcard purchase'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message':'Unable to get transaction'}, status= status.HTTP_400_BAD_REQUEST)
        except Transaction.DoesNotExist:
            return Response({'message': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message':'Method not allowed'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def declineBuyGiftcard(request, pk):
    if request.method == 'POST':
        try:
            transaction= Transaction.objects.get(id=pk, transaction_category='GiftcardPurchase', status='pending')
            if transaction:
                transaction_id= transaction.id
                transaction_amount= transaction.amount
                client_id= transaction.client.id
                client= Client.objects.get(id=client_id)
                client_email= client.email_address
                client_firstName= client.first_name
                client_balance= client.balance
                '''
                subject= "Giftcard Purchase Failed"
                html_message= render_to_string('api/GiftcardPurchaseDeclineMail.html', {'name':client_firstName, 'amount':transaction_amount})
                plain_message= strip_tags(html_message)
                from_email= settings.EMAIL_HOST_USER
                '''
                new_transaction_status= 'failed'
                transaction_update_data= {'status': new_transaction_status}
                client_new_balance= {'balance': float(client_balance) + float(transaction_amount)}
                serializer= ClientTransactionSerializer(transaction, data=transaction_update_data, partial=True)
                client_serializer= ClientSerializer(client, data=client_new_balance, partial=True)
                '''
                try:
                    mail.send_mail(subject, plain_message, from_email, [client_email], html_message=html_message)
                    return Response({'message': 'Crypto Purchase Notification Sent'}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                '''
                if serializer.is_valid() and client_serializer.is_valid():
                    serializer.save()
                    client_serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'message':'Unable to process crypto purchase'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message':'Unable to get transaction'}, status= status.HTTP_400_BAD_REQUEST)
        except Transaction.DoesNotExist:
            return Response({'message': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Method not allowed'}, status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def updateSellGiftcard(request, pk):
    if request.method == 'POST':
        try:
            card_sale= PendingGiftCardSale.objects.get(id=pk)
            if card_sale:
                usd_value= card_sale.giftcard_amount
                naira_value= card_sale.amount
                card_type= card_sale.giftcard_type
                client_id= card_sale.client.id
                request_id= generate_request_id
                if client_id:
                    try:
                        client_info= Client.objects.get(id=client_id)
                        if client_info:
                            new_client_bal= {'balance': float(naira_value) + float(client_info.balance)}
                            update_client_bal= ClientSerializer(client_info, data=new_client_bal, partial=True)
                            if update_client_bal.is_valid():
                                update_client_bal.save()
                                card_sale.delete()
                                Transaction.objects.create(
                                    client= client_info,
                                    transaction_type= f'GiftcardSale - ${usd_value} - {card_type}',
                                    transaction_category= 'GiftcardSale',
                                    transaction_id= request_id,
                                    amount= naira_value,
                                    status= 'completed',
                                )
                                '''
                                subject= "GiftcardSale Sale"
                                html_message= render_to_string('api/GiftcardSaleMail.html', {'name':client_firstName})
                                plain_message= strip_tags(html_message)
                                from_email= settings.EMAIL_HOST_USER

                                try:
                                    mail.send_mail(subject, plain_message, from_email, [client_email], html_message=html_message)
                                    return Response({'message': 'GiftcardSale Notification Sent'}, status=status.HTTP_200_OK)
                                except Exception as e:
                                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                                '''
                                return Response({'message':'Giftcard sale updated'}, status=status.HTTP_200_OK)
                            else:
                                return Response({'message':'Error updating request'}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({'message':'unable to find client'}, status=status.HTTP_404_NOT_FOUND)
                    except Client.DoesNotExist:
                        return Response({'message':'Cannot find client associated with this transaction'}, status= status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'message':'Cannot information not found'}, status= status.HTTP_404_NOT_FOUND)
        except PendingCoinSale.DoesNotExist:
            return Response({'message':'Giftcard sale transaction not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message':'Request not allowed'}, status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def declineSellGiftcard(request, pk):
    if request.method == 'POST':
        try:
            card_sale= PendingGiftCardSale.objects.get(id=pk)
            if card_sale:
                usd_value= card_sale.giftcard_amount
                naira_value= card_sale.amount
                card_type= card_sale.giftcard_type
                client_id= card_sale.client.id
                request_id= generate_request_id
                if client_id:
                    try:
                        client_info= Client.objects.get(id=client_id)
                        if client_info:
                            card_sale.delete()
                            Transaction.objects.create(
                                client= client_info,
                                transaction_type= f'GiftcardSale - ${usd_value} - {card_type}',
                                transaction_category= 'GiftcardSale',
                                transaction_id= request_id,
                                amount= naira_value,
                                status= 'failed',
                            )
                            '''
                            subject= "Giftcard Sale Declined"
                            html_message= render_to_string('api/GiftcardDeclinedMail.html', {'name':client_firstName})
                            plain_message= strip_tags(html_message)
                            from_email= settings.EMAIL_HOST_USER

                            try:
                                mail.send_mail(subject, plain_message, from_email, [client_email], html_message=html_message)
                                return Response({'message': 'Giftcard Sale Declined Notification Sent'}, status=status.HTTP_200_OK)
                            except Exception as e:
                                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                            '''
                            return Response({'message':'Giftcard sale updated'}, status=status.HTTP_200_OK)
                        else:
                            return Response({'message':'unable to find client'}, status=status.HTTP_404_NOT_FOUND)
                    except Client.DoesNotExist:
                        return Response({'message':'Cannot find client associated with this transaction'}, status= status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'message':'information not found'}, status= status.HTTP_404_NOT_FOUND)
        except PendingCoinSale.DoesNotExist:
            return Response({'message':'Giftcard sale transaction not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message':'Request not allowed'}, status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_withdrawal(request, pk):
    if request.method == 'POST':
        try:
            withdrawalInfo= Withdrawal_request.objects.get(id=pk)
            request_id= generate_request_id()
            if withdrawalInfo:
                withdrawalInfo_id= withdrawalInfo.id
                withdrawalInfo_amount= withdrawalInfo.amount
                withdrawalInfo_bank_name= withdrawalInfo.bank_name
                withdrawalInfo_bankaccount_number= withdrawalInfo.bankaccount_number
                client_id= withdrawalInfo.client.id
                client= Client.objects.get(id=client_id)
                client_email= client.email_address
                client_firstName= client.first_name
                '''
                subject= "Withdrawal Notification"
                html_message= render_to_string('api/withdrawalMail.html', {'name':client_firstName})
                plain_message= strip_tags(html_message)
                from_email= settings.EMAIL_HOST_USER
                '''
                Transaction.objects.create(
                    client= client,
                    transaction_type= f'Withdrawal to {withdrawalInfo_bank_name} - {withdrawalInfo_bankaccount_number}',
                    transaction_category= 'Withdrawal',
                    transaction_id= request_id,
                    amount= withdrawalInfo_amount,
                    status= 'completed'
                )
                withdrawalInfo.delete()
                '''
                try:
                    mail.send_mail(subject, plain_message, from_email, [client_email], html_message=html_message)
                    return Response({'message': 'Withdrawal Notification Sent'}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                '''
                return Response({'message':'Withdrawal Processed Successfully'}, status= status.HTTP_200_OK)
            else:
                return Response({'message':'This withdrawal request does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Withdrawal_request.DoesNotExist:
            return Response({'message':'This withdrawal has been attended to'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'message':'Method not allowed'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def decline_withdrawal(request, pk):
    if request.method == 'POST':
        try:
            withdrawalInfo= Withdrawal_request.objects.get(id=pk)
            request_id= generate_request_id()
            if withdrawalInfo:
                withdrawalInfo_id= withdrawalInfo.id
                withdrawalInfo_amount= withdrawalInfo.amount
                withdrawalInfo_bank_name= withdrawalInfo.bank_name
                withdrawalInfo_bankaccount_number= withdrawalInfo.bankaccount_number
                client_id= withdrawalInfo.client.id
                client= Client.objects.get(id=client_id)
                client_email= client.email_address
                client_firstName= client.first_name
                '''
                subject= "Withdrawal Declined"
                html_message= render_to_string('api/withdrawaldeclineMail.html', {'name':client_firstName})
                plain_message= strip_tags(html_message)
                from_email= settings.EMAIL_HOST_USER
                '''
                client_current_balance= float(client.balance) + float(withdrawalInfo_amount)
                client_update_data= {'balance': client_current_balance}
                serializer= ClientSerializer(client, data=client_update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    Transaction.objects.create(
                        client= client,
                        transaction_type= f'Withdrawal to {withdrawalInfo_bank_name} - {withdrawalInfo_bankaccount_number}',
                        transaction_category= 'Withdrawal',
                        transaction_id= request_id,
                        amount= withdrawalInfo_amount,
                        status= 'failed'
                    )
                    withdrawalInfo.delete()
                    '''
                    try:
                        mail.send_mail(subject, plain_message, from_email, [client_email], html_message=html_message)
                        return Response({'message': 'Withdrawal Notification Sent'}, status=status.HTTP_200_OK)
                    except Exception as e:
                        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    '''
                    return Response({'message':'Withdrawal Declined Successfully'}, status= status.HTTP_200_OK)
                else:
                    return Response({'message':'Cannot update client'}, status= status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'This withdrawal does not exist'}, status= status.HTTP_400_BAD_REQUEST)
        except Withdrawal_request.DoesNotExist:
            return Response({'message':'This withdrawal request has been attended to'}, status= status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message":"Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)
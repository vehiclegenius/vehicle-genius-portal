import json
import os
from urllib.parse import quote_plus

import requests as requests
from django.http import HttpResponse
from django.shortcuts import render


def get_ethereum_challenge(request):
    return render(request, 'oauth/get_ethereum_challenge.html')


def generate_challenge(request):
    oauth_host = os.environ.get('OAUTH_HOST')
    host = os.environ.get('HOST')
    body = json.loads(request.body)
    wallet_address = body['wallet_address']
    url = f'{oauth_host}/auth/web3/generate_challenge' \
          f'?client_id=vehicle-genius' \
          f'&domain={quote_plus(f"{host}/oauth/callback")}' \
          f'&scope={quote_plus(f"openid email")}' \
          f'&response_type=code' \
          f'&address={quote_plus(wallet_address)}'

    challenge = requests.post(url)

    return HttpResponse(challenge, content_type='text/plain')


def submit_challenge(request):
    oauth_host = os.environ.get('OAUTH_HOST')
    host = os.environ.get('HOST')
    body = json.loads(request.body)
    url = f'{oauth_host}/auth/web3/submit_challenge'
    data = {
        'client_id': 'vehicle-genius',
        'domain': f'{host}/oauth/callback',
        'grant_type': 'authorization_code',
        'state': body['state'],
        'signature': body['signature'],
    }

    challenge = requests.post(url, data=data)

    return HttpResponse(challenge, content_type='text/plain')


def callback(request):
    print('oauth/callback')
    print(request.POST)

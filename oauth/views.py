import json
import os
from datetime import datetime, timedelta
from urllib.parse import quote_plus

import requests as requests
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


def get_challenge(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('vehicles:index'))

    return render(request, 'oauth/get_challenge.html')


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

    auth_res = requests.post(url, data=data).json()

    if 'access_token' not in auth_res:
        return HttpResponse(status=401, content_type='application/json')

    user_res = requests.get(
        f'{os.environ.get("USERS_API_HOST")}/v1/user',
        headers={'Authorization': f'Bearer {auth_res["access_token"]}'},
    ).json()

    expires_in = datetime.now() + timedelta(seconds=auth_res['expires_in'])
    res = HttpResponse(json.dumps({'success': True}), content_type='application/json')
    res.set_cookie('access_token', auth_res['access_token'], expires=expires_in)
    res.set_cookie('user_id', user_res['web3']['address'], expires=expires_in)

    return res


def callback(request):
    print('oauth/callback')
    print(request.POST)

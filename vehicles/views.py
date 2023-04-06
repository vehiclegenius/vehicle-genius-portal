import json
import os

import requests
from django.shortcuts import render


def index(request):
    if request.method == 'GET':
        return index_get(request)
    elif request.method == 'POST':
        return index_post(request)


def index_post(request):
    data = request.POST
    print(data['vin'], data['prompt'])
    body = {
        'vin': data['vin'],
        'prompt': data['prompt'],
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    response = requests.post(
        os.environ.get('API_BASE_URL') + '/assistant/answer-user-prompt',
        data=json.dumps(body),
        headers=headers)
    answer = response.content.decode('utf-8')
    return render(request, 'vehicles/index.html', {
        'show_answer': True,
        'question': data['prompt'],
        'answer': answer,
    })


def index_get(request):
    return render(request, 'vehicles/index.html')

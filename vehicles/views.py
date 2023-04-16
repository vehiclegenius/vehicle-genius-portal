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
    data = parse_request_post(request.POST)
    print(data['vin'], data['messages'])
    body = {
        'vin': data['vin'],
        'messages': data['messages'],
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    response = requests.post(
        os.environ.get('API_BASE_URL') + '/assistant/answer-user-prompt',
        data=json.dumps(body),
        headers=headers)
    answer = json.loads(response.content.decode('utf-8'))
    return render(request, 'vehicles/index.html', {
        'question': data['messages'][-1]['content'],
        'ai_messages': answer,
    })


def index_get(request):
    return render(request, 'vehicles/index.html')


def parse_request_post(request_post):
    # create a new copy of the request.POST data
    parsed_post = request_post.copy()

    # loop through the keys in the request.POST data
    for key in request_post:
        # check if the key contains an array index
        if '[' in key and ']' in key:
            # extract the key prefix and index from the key name
            key_prefix, index = key.split('[', 1)
            index = index.split(']', 1)[0]
            # create a dictionary for the message
            message = {k.split('.')[1]: v for k, v in request_post.items() if k.startswith(f'{key_prefix}[{index}].')}
            # add the message to the parsed_post dictionary
            parsed_post[key_prefix] = parsed_post.get(key_prefix, []) + [message]

    # remove duplicates from lists in the parsed_post dictionary
    for key, value in parsed_post.items():
        if isinstance(value, list):
            unique_value = []
            for item in value:
                if item not in unique_value:
                    unique_value.append(item)
            parsed_post[key] = unique_value

    return parsed_post

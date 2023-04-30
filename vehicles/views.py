import json
import os

import requests
from django.shortcuts import render


def index_get(request):
    vehicles = make_api_get_request('/vehicles')
    return render(request, 'vehicles/index.html', {'vehicles': vehicles})


def id_get(request, pk: str):
    vehicle = make_api_get_request(f'/vehicles/{pk}')
    return render(request, 'vehicles/id.html', {'vehicle': vehicle})


def answer_user_prompt_post(request):
    data = parse_request_post(request.POST)
    print(data['vin'], data['messages'])
    body = {
        'vehicleId': data['vehicle_id'],
        'messages': data['messages'],
    }
    answer = make_api_post_request('/assistant/answer-user-prompt', body)
    vehicle = make_api_get_request(f'/vehicles/{data["vehicle_id"]}')
    return render(request, 'vehicles/id.html', {
        'question': data['messages'][-1]['content'],
        'ai_messages': answer,
        'vehicle': vehicle,
    })


def make_api_get_request(uri: str):
    headers = {
        'Accept': 'application/json',
    }
    response = requests.get(os.environ.get('API_BASE_URL') + uri, headers=headers)
    answer = json.loads(response.content.decode('utf-8'))
    return answer


def make_api_post_request(uri: str, body):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    response = requests.post(
        os.environ.get('API_BASE_URL') + uri,
        data=json.dumps(body),
        headers=headers)
    answer = json.loads(response.content.decode('utf-8'))
    return answer


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

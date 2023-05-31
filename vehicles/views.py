import json
import os
import uuid

import requests
from django.shortcuts import render, redirect

default_prompts = [
    'How much will my car be worth in 2 years?',
    'What is the car\'s length?',
]


def index(request):
    if request.method == 'GET':
        return index_get(request)
    elif request.method == 'POST':
        new_id = uuid.uuid4()
        body = {
            'id': str(new_id),
            'vin': request.POST['vin'],
        }
        make_api_put_request(f'/vehicles/{new_id}?username={request.user.username}', body)
        return redirect(f'/vehicles/{new_id}')


def index_get(request):
    vehicles = make_api_get_request(f'/vehicles?username={request.user.username}')
    return render(request, 'vehicles/index.html', {'vehicles': vehicles})


def id_get(request, pk: str):
    vehicle = make_api_get_request(f'/vehicles/{pk}?username={request.user.username}')
    return render(request, 'vehicles/id.html', {
        'vehicle': vehicle,
        'default_prompts': default_prompts,
    })


def id_prompt_get(request, pk: str, index: int):
    prompt = default_prompts[index]
    prompt_body = {
        'vehicleId': pk,
        'messages': [{'role': 'user', 'content': prompt}],
    }
    prompt_data = {
        'vehicle_id': pk,
    }
    return answer_user_prompt(prompt_body, prompt_data, request)


def add_get(request):
    return render(request, 'vehicles/add_vehicle.html')


def answer_user_prompt_post(request):
    data = parse_request_post(request.POST)
    body = {
        'vehicleId': data['vehicle_id'],
        'messages': data['messages'] + [{'role': 'user', 'content': data['user_message']}]
    }
    return answer_user_prompt(body, data, request)


def feedback_post(request):
    data = parse_request_post(request.POST)
    if parse_bool(data['is_positive']):
        return render(request, 'vehicles/feedback_positive.html')
    else:
        body = {
            'vehicleId': data['vehicle_id'],
            'messages': data['messages'],
            'isPositive': parse_bool(data['is_positive']),
            'reason': data['reason'],
            'username': request.user.username,
        }
        make_api_post_request('/assistant/prompt/feedback', body)
        return render(request, 'vehicles/feedback_negative.html')


def answer_user_prompt(body, data, request):
    body['username'] = request.user.username
    answer = make_api_post_request('/assistant/prompt/answer', body)
    vehicle = make_api_get_request(f'/vehicles/{data["vehicle_id"]}?username={request.user.username}')
    return render(request, 'vehicles/id.html', {
        'conversation': answer,
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
    if response.content:
        answer = json.loads(response.content.decode('utf-8'))
        return answer
    else:
        return None


def make_api_put_request(uri: str, body):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    response = requests.put(
        os.environ.get('API_BASE_URL') + uri,
        data=json.dumps(body),
        headers=headers)
    return response


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


def parse_bool(value):
    if value.lower() in ['true', 't', 'yes', 'y', '1']:
        return True
    elif value.lower() in ['false', 'f', 'no', 'n', '0']:
        return False
    else:
        raise ValueError(f'Could not parse boolean value: {value}')

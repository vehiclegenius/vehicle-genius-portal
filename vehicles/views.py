import json
import os
import uuid

import requests
from django.shortcuts import render, redirect
from django.contrib import messages

from vehicles.forms import VehicleUserDataForm

default_prompts = [
    'I need maintenance advice 🛠️',
    'Help me with my car finances 💰',
    'Is my insurance fair 🤷',
    'I\'m thinking about buying or selling a car 🚙',
    'I want to hear a fun fact about my car 😎',
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
        response = make_api_put_request(f'/vehicles/{new_id}?username={request.user.username}', body)
        final_id = json.loads(response.content.decode('utf-8'))
        return redirect(f'/vehicles/{final_id}')


def index_get(request):
    vehicles = make_api_get_request(f'/vehicles?username={request.user.username}')
    return render(request, 'vehicles/index.html', {'vehicles': vehicles})


def id_chatbot_get(request, pk: str):
    vehicle = make_api_get_request(f'/vehicles/{pk}?username={request.user.username}')
    return render(request, 'vehicles/chatbot.html', {
        'vehicle': vehicle,
        'default_prompts': default_prompts,
    })


def id_get(request, pk: str):
    vehicle = make_api_get_request(f'/vehicles/{pk}?username={request.user.username}')
    return render(request, 'vehicles/id.html', {'vehicle': vehicle})


def id_edit(request, pk: str):
    vehicle = make_api_get_request(f'/vehicles/{pk}?username={request.user.username}')

    if request.method == 'POST':
        form = VehicleUserDataForm(request.POST)
        if form.is_valid():
            vehicle['userData'] = {
                'insuranceRate': form['insurance_rate'].data,
                'insuranceProvider': form['insurance_provider'].data,
                'insuranceRenewalDate': form['insurance_renewal_date'].data,
                'financingInterestRate': form['financing_interest_rate'].data,
                'financingTermEnd': form['financing_term_end'].data,
                'previousMaintenanceData': form['previous_maintenance_data'].data,
            }
            del vehicle['vinAuditData']
            make_api_put_request(f'/vehicles/{pk}?username={request.user.username}', vehicle)
            messages.success(request, 'Vehicle updated successfully')
        else:
            messages.error(request, 'Invalid data')
    else:
        user_data = vehicle['userData']
        initial_data = {
            'insurance_rate': user_data['insuranceRate'],
            'insurance_provider': user_data['insuranceProvider'],
            'insurance_renewal_date': user_data['insuranceRenewalDate'],
            'financing_interest_rate': user_data['financingInterestRate'],
            'financing_term_end': user_data['financingTermEnd'],
            'previous_maintenance_data': user_data['previousMaintenanceData'],
        }
        form = VehicleUserDataForm(initial=initial_data)

    vehicle = make_api_get_request(f'/vehicles/{pk}?username={request.user.username}')
    return render(request, 'vehicles/edit.html', {'vehicle': vehicle, 'form': form})


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
    added_vehicles = make_api_get_request(f'/vehicles?username={request.user.username}')
    added_vehicle_vins = [vehicle['vin'].lower() for vehicle in added_vehicles]
    owned_vehicles = make_dimo_api_get_request(request, f'{os.environ.get("DEVICES_API_HOST")}/v1/user/devices/me')
    owned_vehicles_data = [
        {
            'vin': vehicle['vin'],
            'name': vehicle['deviceDefinition']['name'],
            'token_id': vehicle['nft']['tokenId'],
        } for vehicle in owned_vehicles['userDevices'] if vehicle['vin'] is not None and vehicle['nft'] is not None and vehicle['nft']['tokenId']  and vehicle['vin'].lower() not in added_vehicle_vins
    ]
    with open('vehicles/abi.json') as abi:
        return render(request, 'vehicles/add_vehicle.html', {
            'owned_vehicles': owned_vehicles_data,
            'abi': json.load(abi),
            'contract_address': os.environ.get('DIMO_CONTRACT_ADDRESS'),
            'target_wallet_address': os.environ.get('SHARE_TARGET_WALLET_ADDRESS'),
        })


def add_fetch_post(request, pk: str):
    vin = pk
    response = make_api_post_request(f'/vehicles/{vin}/fetch-dimo?username={request.user.username}', {})
    return redirect(f'/vehicles')


def answer_user_prompt_post(request):
    data = parse_request_post(request.POST)
    if not 'messages' in data:
        data['messages'] = []
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
    return render(request, 'vehicles/chatbot.html', {
        'conversation': answer,
        'vehicle': vehicle,
    })


def make_dimo_api_get_request(request, url: str):
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {request.COOKIES.get("access_token")}',
    }
    response = requests.get(url, headers=headers)
    if response.content:
        try:
            answer = json.loads(response.content.decode('utf-8'))
            return answer
        except json.JSONDecodeError:
            raise Exception(response.content.decode('utf-8'))


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
        try:
            answer = json.loads(response.content.decode('utf-8'))
            return answer
        except json.JSONDecodeError:
            raise Exception(response.content.decode('utf-8'))
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
    if response.content:
        try:
            json.loads(response.content.decode('utf-8'))
            return response
        except json.JSONDecodeError:
            raise Exception(response.content.decode('utf-8'))


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

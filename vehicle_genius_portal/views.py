from django.shortcuts import redirect


def redirect_to_vehicles(request):
    return redirect('/vehicles')

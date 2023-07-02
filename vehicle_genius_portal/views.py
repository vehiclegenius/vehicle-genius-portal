from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect


def redirect_to_vehicles(request):
    return redirect('/vehicles')


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        # Call the parent's dispatch method to execute the default logout routine
        response = super().dispatch(request, *args, **kwargs)

        # Perform your additional step after logout
        response.delete_cookie('access_token')
        response.delete_cookie('user_id')

        # Return the response or redirect to a desired URL
        return response

    def get_next_page(self):
        # Define the URL to redirect to after logout
        return '/'

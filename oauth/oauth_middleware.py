from oauth.user_model import User


class OAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'user_id' in request.COOKIES and 'access_token' in request.COOKIES:
            request.user = User()
            request.user.is_authenticated = True
            request.user.user_id = request.COOKIES['user_id']
            request.user.username = request.COOKIES['user_id']
            request.user.access_token = request.COOKIES['access_token']

        response = self.get_response(request)
        return response

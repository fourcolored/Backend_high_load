from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from tasks.jwt import validate_jwt


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.COOKIES.get('jwt_token')
        if token:
            try:
                payload = validate_jwt(token)
                request.user_id = payload['user_id']
            except PermissionDenied as e:
                response =  JsonResponse({'error': str(e)}, status=403)
                response.delete_cookie('jwt_token')
                return response
            except Exception as e:
                # Catch other unforeseen errors
                return JsonResponse({'error': str(e)}, status=500)
        return None
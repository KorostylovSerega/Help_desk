from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.authtoken.models import Token


class CustomTokenAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_data = get_authorization_header(request).split()

        if not auth_data or auth_data[0].lower() != b'token':
            return None

        if len(auth_data) == 1:
            message = 'Invalid token header. No authenticate data.'
            raise exceptions.AuthenticationFailed(message)
        elif len(auth_data) > 2:
            message = 'Invalid token header. Authenticate data should not contain spaces.'
            raise exceptions.AuthenticationFailed(message)

        try:
            key = auth_data[1].decode()
        except UnicodeError:
            message = 'Invalid token header. Token key should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(message)

        try:
            token = Token.objects.select_related('user').get(key=key)
        except Token.DoesNotExist:
            message = 'Invalid token.'
            raise exceptions.AuthenticationFailed(message)

        user = token.user

        if not user.is_active:
            message = 'User inactive or deleted.'
            raise exceptions.AuthenticationFailed(message)

        # token_life_time = (timezone.now() - token.created).seconds
        #
        # if token_life_time > TOKEN_LIFE_TIME_LIMIT:
        #     message = f'The token has expired. Please generate a new token in {TOKEN_GENERATE_LINK}'
        #     raise exceptions.AuthenticationFailed(message)

        return user, token

from django.core.cache import cache
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from config.settings import TOKEN_EXPIRATION_TIME


class CustomTokenAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')

        time_now = timezone.now()
        last_activity_time = cache.get(key, time_now)
        inactivity_period = time_now - last_activity_time

        if inactivity_period.seconds > TOKEN_EXPIRATION_TIME:
            token.delete()
            cache.delete(key)
            raise AuthenticationFailed('Token has expired.')

        cache.set(key, time_now)
        return token.user, token

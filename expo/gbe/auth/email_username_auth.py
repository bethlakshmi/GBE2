from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailUsernameAuth(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    Recognizes EITHER Uername or Password
    """

    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            users = UserModel.objects.filter(
                Q(username=username) | Q(email=username))
            for user in users:
                if user.check_password(password):
                    return user
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
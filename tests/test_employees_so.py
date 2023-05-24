import pytest
from django.contrib.auth.models import User


@pytest.fixture
def admin_user() -> User:
    return User.objects.get(username="admin")




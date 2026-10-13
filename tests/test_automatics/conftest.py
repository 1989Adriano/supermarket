import pytest

from core.security import require_admin
from main import app


async def allow_admin_in_route_tests() -> dict[str, str]:
    return {"sub": "test-admin", "role": "admin"}


@pytest.fixture(autouse=True)
def override_auth_for_route_tests():
    app.dependency_overrides[require_admin] = allow_admin_in_route_tests
    yield
    app.dependency_overrides.pop(require_admin, None)

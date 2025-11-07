"""
Pytest configuration and fixtures for the icosa test suite.
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


@pytest.fixture
def client():
    """Django test client fixture."""
    return Client()


@pytest.fixture
def authenticated_client(db, user):
    """Authenticated Django test client fixture."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def user(db):
    """Create a regular user for testing."""
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123',
        displayname='Test User'
    )


@pytest.fixture
def superuser(db):
    """Create a superuser for testing."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        displayname='Admin User'
    )


@pytest.fixture
def users(db):
    """Create multiple users for testing."""
    return [
        User.objects.create_user(
            username=f'user{i}',
            email=f'user{i}@example.com',
            password=f'pass{i}',
            displayname=f'User {i}'
        )
        for i in range(1, 4)
    ]


@pytest.fixture
def sample_image():
    """Create a sample image file for testing uploads."""
    # 1x1 pixel red PNG
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf'
        b'\xc0\x00\x00\x00\x03\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return SimpleUploadedFile('test_image.png', png_data, content_type='image/png')


@pytest.fixture
def sample_glb_file():
    """Create a sample GLB file for testing uploads."""
    # Minimal valid GLB header
    glb_data = (
        b'glTF'  # Magic
        b'\x02\x00\x00\x00'  # Version 2
        b'\x0c\x00\x00\x00'  # Length 12 bytes
    )
    return SimpleUploadedFile('test_model.glb', glb_data, content_type='model/gltf-binary')


@pytest.fixture
def api_client():
    """API client fixture for testing REST endpoints."""
    return Client()


@pytest.fixture
def authenticated_api_client(db, user):
    """Authenticated API client fixture."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests by default."""
    pass


@pytest.fixture
def mock_storage(mocker):
    """Mock storage backend for testing file uploads."""
    mock = mocker.patch('django.core.files.storage.default_storage.save')
    mock.return_value = 'test_file_path.glb'
    return mock

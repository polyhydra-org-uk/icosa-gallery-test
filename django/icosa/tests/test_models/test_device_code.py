"""
Tests for the DeviceCode model.
"""
import pytest
from django.utils import timezone
from datetime import timedelta

from icosa.models import DeviceCode
from icosa.tests.fixtures.factories import (
    DeviceCodeFactory,
    UserFactory,
)


@pytest.mark.django_db
@pytest.mark.models
class TestDeviceCodeModel:
    """Test suite for DeviceCode model."""

    def test_create_device_code(self):
        """Test creating a device code."""
        device_code = DeviceCodeFactory()
        assert device_code.id is not None
        assert device_code.user is not None
        assert device_code.devicecode is not None
        assert device_code.expiry is not None

    def test_device_code_string_representation(self):
        """Test string representation of device code."""
        user = UserFactory()
        expiry = timezone.now() + timedelta(hours=1)
        device_code = DeviceCodeFactory(
            user=user,
            devicecode='ABC123',
            expiry=expiry
        )

        str_repr = str(device_code)
        assert 'ABC123' in str_repr
        assert str(expiry) in str_repr

    def test_device_code_max_length(self):
        """Test device code max length is 6 characters."""
        device_code = DeviceCodeFactory(devicecode='123456')
        assert len(device_code.devicecode) == 6

    def test_device_code_user_relationship(self):
        """Test device code belongs to a user."""
        user = UserFactory()
        device_code = DeviceCodeFactory(user=user)

        assert device_code.user == user
        assert device_code in DeviceCode.objects.filter(user=user)

    def test_device_code_expiry_field(self):
        """Test device code expiry field."""
        expiry = timezone.now() + timedelta(hours=2)
        device_code = DeviceCodeFactory(expiry=expiry)

        assert device_code.expiry == expiry

    def test_device_code_is_valid_when_not_expired(self):
        """Test device code is valid when not expired."""
        device_code = DeviceCodeFactory(
            expiry=timezone.now() + timedelta(hours=1)
        )

        # Code should not be expired
        assert device_code.expiry > timezone.now()

    def test_device_code_is_expired_when_past_expiry(self):
        """Test device code is expired when past expiry time."""
        device_code = DeviceCodeFactory(
            expiry=timezone.now() - timedelta(hours=1)
        )

        # Code should be expired
        assert device_code.expiry < timezone.now()

    def test_device_code_query_valid_codes(self):
        """Test querying for valid (non-expired) device codes."""
        valid_code = DeviceCodeFactory(
            devicecode='VALID',
            expiry=timezone.now() + timedelta(hours=1)
        )
        expired_code = DeviceCodeFactory(
            devicecode='EXPIRED',
            expiry=timezone.now() - timedelta(hours=1)
        )

        # Query for valid codes
        valid_codes = DeviceCode.objects.filter(expiry__gt=timezone.now())

        assert valid_code in valid_codes
        assert expired_code not in valid_codes

    def test_device_code_query_by_code(self):
        """Test querying device code by devicecode field."""
        device_code = DeviceCodeFactory(devicecode='QUERY123')

        found = DeviceCode.objects.filter(devicecode='QUERY123').first()

        assert found == device_code

    def test_device_code_query_case_insensitive(self):
        """Test querying device code with case-insensitive search."""
        device_code = DeviceCodeFactory(devicecode='CaSe123')

        # Query case-insensitively
        found = DeviceCode.objects.filter(devicecode__iexact='case123').first()

        assert found == device_code

    def test_device_code_user_cascade_delete(self):
        """Test that deleting user cascades to delete device codes."""
        user = UserFactory()
        device_code = DeviceCodeFactory(user=user)

        code_id = device_code.id
        user.delete()

        # Device code should be deleted
        assert not DeviceCode.objects.filter(id=code_id).exists()

    def test_device_code_multiple_codes_per_user(self):
        """Test that user can have multiple device codes."""
        user = UserFactory()
        code1 = DeviceCodeFactory(user=user, devicecode='CODE1')
        code2 = DeviceCodeFactory(user=user, devicecode='CODE2')

        user_codes = DeviceCode.objects.filter(user=user)

        assert user_codes.count() == 2
        assert code1 in user_codes
        assert code2 in user_codes

    def test_device_code_deletion(self):
        """Test deleting a device code."""
        device_code = DeviceCodeFactory()
        code_id = device_code.id

        device_code.delete()

        assert not DeviceCode.objects.filter(id=code_id).exists()

    def test_device_code_short_expiry(self):
        """Test device code with short expiry (e.g., 5 minutes)."""
        expiry = timezone.now() + timedelta(minutes=5)
        device_code = DeviceCodeFactory(expiry=expiry)

        # Should be valid for now
        assert device_code.expiry > timezone.now()

        # Time difference should be approximately 5 minutes
        time_diff = (device_code.expiry - timezone.now()).total_seconds()
        assert 290 < time_diff < 310  # ~5 minutes with some tolerance

    def test_device_code_long_expiry(self):
        """Test device code with long expiry (e.g., 24 hours)."""
        expiry = timezone.now() + timedelta(hours=24)
        device_code = DeviceCodeFactory(expiry=expiry)

        # Should be valid
        assert device_code.expiry > timezone.now()

        # Time difference should be approximately 24 hours
        time_diff = (device_code.expiry - timezone.now()).total_seconds()
        assert time_diff > 86000  # ~24 hours

    def test_device_code_alphanumeric(self):
        """Test device code contains alphanumeric characters."""
        device_code = DeviceCodeFactory(devicecode='A1B2C3')

        assert device_code.devicecode.isalnum()

    def test_device_code_unique_per_user(self):
        """Test that same code string can be used for different users."""
        user1 = UserFactory()
        user2 = UserFactory()

        # Same code for different users
        code1 = DeviceCodeFactory(user=user1, devicecode='SHARED')
        code2 = DeviceCodeFactory(user=user2, devicecode='SHARED')

        # Both should exist
        assert DeviceCode.objects.filter(devicecode='SHARED').count() == 2

    def test_device_code_exact_expiry_matching(self):
        """Test querying with exact expiry time."""
        expiry = timezone.now() + timedelta(hours=1)
        device_code = DeviceCodeFactory(
            devicecode='EXACT',
            expiry=expiry
        )

        # Query with exact expiry
        found = DeviceCode.objects.filter(
            devicecode='EXACT',
            expiry=expiry
        ).first()

        assert found == device_code

    def test_device_code_get_or_create(self):
        """Test get_or_create pattern with device codes."""
        user = UserFactory()

        # Create new code
        code1, created1 = DeviceCode.objects.get_or_create(
            user=user,
            devicecode='GETORCREATE',
            defaults={'expiry': timezone.now() + timedelta(hours=1)}
        )

        assert created1 is True

        # Get existing code
        code2, created2 = DeviceCode.objects.get_or_create(
            user=user,
            devicecode='GETORCREATE',
            defaults={'expiry': timezone.now() + timedelta(hours=1)}
        )

        assert created2 is False
        assert code1 == code2

    def test_device_code_count_by_user(self):
        """Test counting device codes for a user."""
        user = UserFactory()

        # Create multiple codes
        for i in range(5):
            DeviceCodeFactory(user=user, devicecode=f'CODE{i}')

        count = DeviceCode.objects.filter(user=user).count()
        assert count == 5

    def test_device_code_filtering_by_validity(self):
        """Test filtering codes by validity period."""
        now = timezone.now()

        # Valid code
        valid = DeviceCodeFactory(
            devicecode='VALID',
            expiry=now + timedelta(hours=1)
        )

        # Expired code
        expired = DeviceCodeFactory(
            devicecode='EXPIRED',
            expiry=now - timedelta(hours=1)
        )

        # Soon to expire
        soon = DeviceCodeFactory(
            devicecode='SOON',
            expiry=now + timedelta(minutes=5)
        )

        # Query valid codes
        valid_codes = DeviceCode.objects.filter(expiry__gt=now)
        assert valid in valid_codes
        assert soon in valid_codes
        assert expired not in valid_codes

        # Query expired codes
        expired_codes = DeviceCode.objects.filter(expiry__lte=now)
        assert expired in expired_codes
        assert valid not in expired_codes

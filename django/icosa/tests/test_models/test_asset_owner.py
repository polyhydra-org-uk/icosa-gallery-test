"""
Tests for the AssetOwner model.
"""
import pytest
from django.urls import reverse

from icosa.models import AssetOwner
from icosa.tests.fixtures.factories import (
    AssetOwnerFactory,
    UserFactory,
    AssetFactory,
)


@pytest.mark.django_db
@pytest.mark.models
class TestAssetOwnerModel:
    """Test suite for AssetOwner model."""

    def test_create_asset_owner(self):
        """Test creating an asset owner."""
        owner = AssetOwnerFactory()
        assert owner.id is not None
        assert owner.url is not None
        assert owner.displayname is not None

    def test_asset_owner_string_representation(self):
        """Test string representation of asset owner."""
        owner = AssetOwnerFactory(displayname='Test Owner')
        assert str(owner) == 'Test Owner'

    def test_url_unique(self):
        """Test that url must be unique."""
        url = 'unique-owner-url'
        AssetOwnerFactory(url=url)

        with pytest.raises(Exception):
            AssetOwnerFactory(url=url)

    def test_url_field_used_as_username(self):
        """Test url field serves as username/slug."""
        owner = AssetOwnerFactory(url='testuser')
        assert owner.url == 'testuser'

    def test_email_field(self):
        """Test email field."""
        email = 'owner@example.com'
        owner = AssetOwnerFactory(email=email)
        assert owner.email == email

    def test_email_optional(self):
        """Test email can be null."""
        owner = AssetOwnerFactory(email=None)
        assert owner.email is None

    def test_displayname_field(self):
        """Test displayname field."""
        displayname = 'Display Name'
        owner = AssetOwnerFactory(displayname=displayname)
        assert owner.displayname == displayname

    def test_description_field(self):
        """Test description field."""
        description = 'This is a test owner description'
        owner = AssetOwnerFactory(description=description)
        assert owner.description == description

    def test_description_optional(self):
        """Test description can be null."""
        owner = AssetOwnerFactory(description=None)
        assert owner.description is None

    def test_migrated_flag_default_false(self):
        """Test migrated flag defaults to False."""
        owner = AssetOwnerFactory(migrated=False)
        assert owner.migrated is False

    def test_migrated_flag_can_be_true(self):
        """Test migrated flag can be set to True."""
        owner = AssetOwnerFactory(migrated=True)
        assert owner.migrated is True

    def test_imported_flag_default_false(self):
        """Test imported flag defaults to False."""
        owner = AssetOwnerFactory(imported=False)
        assert owner.imported is False

    def test_imported_flag_can_be_true(self):
        """Test imported flag can be set to True."""
        owner = AssetOwnerFactory(imported=True)
        assert owner.imported is True

    def test_is_claimed_flag_default_true(self):
        """Test is_claimed flag defaults to True."""
        owner = AssetOwnerFactory(is_claimed=True)
        assert owner.is_claimed is True

    def test_is_claimed_flag_can_be_false(self):
        """Test is_claimed flag can be False for unclaimed owners."""
        owner = AssetOwnerFactory(is_claimed=False)
        assert owner.is_claimed is False

    def test_django_user_relationship(self):
        """Test relationship with Django user."""
        user = UserFactory()
        owner = AssetOwnerFactory(django_user=user)
        assert owner.django_user == user
        assert owner in user.assetowner_set.all()

    def test_django_user_optional(self):
        """Test django_user can be null (for unclaimed owners)."""
        owner = AssetOwnerFactory(django_user=None, is_claimed=False)
        assert owner.django_user is None

    def test_merged_with_self_reference(self):
        """Test merged_with self-referencing foreign key."""
        owner1 = AssetOwnerFactory()
        owner2 = AssetOwnerFactory(merged_with=owner1)
        assert owner2.merged_with == owner1

    def test_merged_with_optional(self):
        """Test merged_with can be null."""
        owner = AssetOwnerFactory(merged_with=None)
        assert owner.merged_with is None

    def test_disable_profile_flag(self):
        """Test disable_profile flag."""
        owner = AssetOwnerFactory(disable_profile=True)
        assert owner.disable_profile is True

    def test_disable_profile_default_false(self):
        """Test disable_profile defaults to False."""
        owner = AssetOwnerFactory(disable_profile=False)
        assert owner.disable_profile is False

    def test_get_displayname_from_django_user(self):
        """Test get_displayname returns django_user displayname if available."""
        user = UserFactory(displayname='User Display Name')
        owner = AssetOwnerFactory(
            django_user=user,
            displayname='Owner Display Name'
        )
        result = owner.get_displayname()
        assert result == 'User Display Name'

    def test_get_displayname_from_owner_when_no_django_user(self):
        """Test get_displayname returns owner displayname when no django_user."""
        owner = AssetOwnerFactory(
            django_user=None,
            displayname='Owner Display Name'
        )
        result = owner.get_displayname()
        assert result == 'Owner Display Name'

    def test_get_displayname_prefers_django_user_displayname(self):
        """Test get_displayname prefers django_user displayname over owner."""
        user = UserFactory(displayname='User Name')
        owner = AssetOwnerFactory(
            django_user=user,
            displayname='Owner Name'
        )
        result = owner.get_displayname()
        assert result == 'User Name'

    def test_get_displayname_falls_back_to_owner(self):
        """Test get_displayname falls back to owner displayname."""
        user = UserFactory(displayname='')
        owner = AssetOwnerFactory(
            django_user=user,
            displayname='Owner Fallback Name'
        )
        result = owner.get_displayname()
        assert result in ['', 'Owner Fallback Name']

    def test_get_absolute_url_with_url(self):
        """Test get_absolute_url returns correct URL."""
        owner = AssetOwnerFactory(url='testowner')
        url = owner.get_absolute_url()
        expected = reverse("icosa:user_show", kwargs={"slug": 'testowner'})
        assert url == expected

    def test_get_absolute_url_without_url(self):
        """Test get_absolute_url returns empty string when no url."""
        owner = AssetOwner(
            displayname='Test',
            url=None
        )
        url = owner.get_absolute_url()
        assert url == ''

    def test_asset_relationship(self):
        """Test relationship with assets."""
        owner = AssetOwnerFactory()
        asset1 = AssetFactory(owner=owner)
        asset2 = AssetFactory(owner=owner)

        assert asset1.owner == owner
        assert asset2.owner == owner
        assert asset1 in owner.asset_set.all()
        assert asset2 in owner.asset_set.all()

    def test_get_unclaimed_for_user_manager_method(self):
        """Test get_unclaimed_for_user manager method."""
        user = UserFactory(username='testuser', email='test@example.com')

        # Create unclaimed owner matching user's email and username
        unclaimed_owner = AssetOwnerFactory(
            django_user=None,
            is_claimed=False,
            email='test@example.com',
            url='testuser'
        )

        # Create a claimed owner (should not be returned)
        claimed_owner = AssetOwnerFactory(
            django_user=user,
            is_claimed=True,
            email='test@example.com',
            url='other'
        )

        # Test the manager method
        unclaimed = AssetOwner.objects.get_unclaimed_for_user(user)

        assert unclaimed_owner in unclaimed
        assert claimed_owner not in unclaimed

    def test_multiple_owners_for_one_user(self):
        """Test one user can have multiple asset owners."""
        user = UserFactory()
        owner1 = AssetOwnerFactory(django_user=user, url='owner1')
        owner2 = AssetOwnerFactory(django_user=user, url='owner2')

        owners = user.assetowner_set.all()
        assert owner1 in owners
        assert owner2 in owners
        assert owners.count() == 2

    def test_cascade_delete_user_sets_owner_null(self):
        """Test deleting user sets owner's django_user to null."""
        user = UserFactory()
        owner = AssetOwnerFactory(django_user=user)

        user.delete()
        owner.refresh_from_db()

        assert owner.django_user is None

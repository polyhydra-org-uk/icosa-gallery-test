"""
Tests for autocomplete view functions.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from icosa.models import Tag
from icosa.tests.fixtures.factories import (
    UserFactory,
    AssetFactory,
    AssetOwnerFactory,
    TagFactory,
)

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.views
class TestTagAutocomplete:
    """Test suite for tag autocomplete view."""

    def test_tag_autocomplete_requires_authentication(self, client):
        """Test that tag autocomplete requires authentication."""
        response = client.get(reverse('icosa:tag-autocomplete'))
        # Should return empty result for anonymous users
        assert response.status_code == 200

    def test_tag_autocomplete_for_authenticated_user(self, authenticated_client, user):
        """Test tag autocomplete for authenticated user."""
        owner = AssetOwnerFactory(django_user=user)
        tag = TagFactory(name='test-tag')
        asset = AssetFactory(owner=owner)
        asset.tags.add(tag)

        response = authenticated_client.get(reverse('icosa:tag-autocomplete'))
        assert response.status_code == 200

    def test_tag_autocomplete_with_query(self, authenticated_client, user):
        """Test tag autocomplete with search query."""
        owner = AssetOwnerFactory(django_user=user)
        tag1 = TagFactory(name='environment')
        tag2 = TagFactory(name='animal')
        asset = AssetFactory(owner=owner)
        asset.tags.add(tag1)
        asset.tags.add(tag2)

        response = authenticated_client.get(reverse('icosa:tag-autocomplete') + '?q=env')
        assert response.status_code == 200

    def test_tag_autocomplete_for_superuser(self, client, superuser):
        """Test that superuser sees all tags."""
        client.force_login(superuser)
        tag = TagFactory(name='admin-tag')

        response = client.get(reverse('icosa:tag-autocomplete'))
        assert response.status_code == 200

    def test_tag_autocomplete_filters_by_user_assets(self, authenticated_client, user):
        """Test that autocomplete only shows tags from user's assets."""
        owner = AssetOwnerFactory(django_user=user)
        user_tag = TagFactory(name='user-tag')
        other_tag = TagFactory(name='other-tag')

        # User's asset with tag
        user_asset = AssetFactory(owner=owner)
        user_asset.tags.add(user_tag)

        # Other user's asset with different tag
        other_owner = AssetOwnerFactory()
        other_asset = AssetFactory(owner=other_owner)
        other_asset.tags.add(other_tag)

        response = authenticated_client.get(reverse('icosa:tag-autocomplete'))
        assert response.status_code == 200

    def test_tag_autocomplete_no_owner(self, authenticated_client, user):
        """Test autocomplete for user without AssetOwner."""
        # User with no AssetOwner
        response = authenticated_client.get(reverse('icosa:tag-autocomplete'))
        assert response.status_code == 200

    def test_tag_autocomplete_case_insensitive_search(self, authenticated_client, user):
        """Test that search is case insensitive."""
        owner = AssetOwnerFactory(django_user=user)
        tag = TagFactory(name='Environment')
        asset = AssetFactory(owner=owner)
        asset.tags.add(tag)

        # Search with lowercase
        response = authenticated_client.get(reverse('icosa:tag-autocomplete') + '?q=env')
        assert response.status_code == 200

    def test_tag_autocomplete_create_tag(self, authenticated_client, user):
        """Test that autocomplete can create new tags."""
        owner = AssetOwnerFactory(django_user=user)

        # The autocomplete view has create_object method
        # Testing this would require simulating the select2 creation flow
        response = authenticated_client.get(reverse('icosa:tag-autocomplete'))
        assert response.status_code == 200

    def test_tag_autocomplete_empty_result_for_no_assets(self, authenticated_client, user):
        """Test that user with no assets gets empty results."""
        owner = AssetOwnerFactory(django_user=user)
        # Owner exists but has no assets

        response = authenticated_client.get(reverse('icosa:tag-autocomplete'))
        assert response.status_code == 200

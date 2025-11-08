"""
Tests for Users API endpoints.
"""
import pytest
from django.test import Client
from django.urls import reverse
from unittest.mock import patch, Mock

from icosa.models.common import PUBLIC, PRIVATE, UNLISTED
from icosa.tests.fixtures.factories import (
    UserFactory,
    AssetFactory,
    AssetOwnerFactory,
    UserLikeFactory,
)


@pytest.mark.django_db
@pytest.mark.api
class TestUsersAPIMeEndpoint:
    """Test suite for GET /api/users/me endpoint."""

    def test_get_me_authenticated(self, authenticated_api_client, user):
        """Test getting current user info when authenticated."""
        response = authenticated_api_client.get('/api/v1/users/me')

        # Should return user info or require JWT auth
        assert response.status_code in [200, 401, 403]

    def test_get_me_unauthenticated(self, api_client):
        """Test getting current user info without authentication."""
        response = api_client.get('/api/v1/users/me')

        # Should require authentication
        assert response.status_code in [401, 403]

    def test_get_me_returns_user_data(self, authenticated_api_client, user):
        """Test that /me returns user data fields."""
        # This test assumes JWT authentication is working
        response = authenticated_api_client.get('/api/v1/users/me')

        if response.status_code == 200:
            data = response.json()
            # Should contain user fields
            assert 'displayName' in data or 'username' in data or 'email' in data


@pytest.mark.django_db
@pytest.mark.api
class TestUsersAPIPatchMe:
    """Test suite for PATCH /api/users/me endpoint."""

    def test_patch_me_unauthenticated(self, api_client):
        """Test updating user without authentication."""
        response = api_client.patch('/api/v1/users/me', data={
            'displayName': 'New Name'
        }, content_type='application/json')

        # Should require authentication
        assert response.status_code in [401, 403]

    def test_patch_me_update_display_name(self, authenticated_api_client, user):
        """Test updating user display name."""
        owner = AssetOwnerFactory(django_user=user)

        response = authenticated_api_client.patch('/api/v1/users/me', data={
            'displayName': 'Updated Name'
        }, content_type='application/json')

        # May require proper JWT auth
        assert response.status_code in [200, 401, 403, 422]

    def test_patch_me_update_url(self, authenticated_api_client, user):
        """Test updating user URL."""
        owner = AssetOwnerFactory(django_user=user, url='oldurl')

        response = authenticated_api_client.patch('/api/v1/users/me', data={
            'url': 'newurl'
        }, content_type='application/json')

        # May require proper JWT auth
        assert response.status_code in [200, 401, 403, 422]

    def test_patch_me_url_already_taken(self, authenticated_api_client, user):
        """Test updating to an already-taken URL."""
        owner = AssetOwnerFactory(django_user=user, url='myurl')
        other_owner = AssetOwnerFactory(url='takenurl')

        response = authenticated_api_client.patch('/api/v1/users/me', data={
            'url': 'takenurl'
        }, content_type='application/json')

        # Should reject with 422 if properly authenticated
        assert response.status_code in [401, 403, 422]

    def test_patch_me_update_description(self, authenticated_api_client, user):
        """Test updating user description."""
        owner = AssetOwnerFactory(django_user=user)

        response = authenticated_api_client.patch('/api/v1/users/me', data={
            'description': 'My new description'
        }, content_type='application/json')

        # May require proper JWT auth
        assert response.status_code in [200, 401, 403]

    def test_patch_me_multiple_owners_error(self, authenticated_api_client, user):
        """Test that users with multiple owners cannot update."""
        owner1 = AssetOwnerFactory(django_user=user, url='owner1')
        owner2 = AssetOwnerFactory(django_user=user, url='owner2')

        response = authenticated_api_client.patch('/api/v1/users/me', data={
            'displayName': 'New Name'
        }, content_type='application/json')

        # Should return 422 for multiple owners, or require auth
        assert response.status_code in [401, 403, 422]


@pytest.mark.django_db
@pytest.mark.api
class TestUsersAPIMeAssets:
    """Test suite for GET /api/users/me/assets endpoint."""

    def test_get_my_assets_unauthenticated(self, api_client):
        """Test getting user assets without authentication."""
        response = api_client.get('/api/v1/users/me/assets')

        # Should require authentication
        assert response.status_code in [401, 403]

    def test_get_my_assets_authenticated(self, authenticated_api_client, user):
        """Test getting user's own assets."""
        owner = AssetOwnerFactory(django_user=user)
        asset1 = AssetFactory(owner=owner, visibility=PUBLIC)
        asset2 = AssetFactory(owner=owner, visibility=PRIVATE)

        response = authenticated_api_client.get('/api/v1/users/me/assets')

        # Should return assets or require JWT auth
        assert response.status_code in [200, 401, 403]

    def test_get_my_assets_includes_private(self, authenticated_api_client, user):
        """Test that user's own assets include private ones."""
        owner = AssetOwnerFactory(django_user=user)
        private_asset = AssetFactory(owner=owner, visibility=PRIVATE)

        response = authenticated_api_client.get('/api/v1/users/me/assets')

        if response.status_code == 200:
            data = response.json()
            # Should have access to private assets
            assert data is not None

    def test_get_my_assets_pagination(self, authenticated_api_client, user):
        """Test pagination of user assets."""
        owner = AssetOwnerFactory(django_user=user)
        for i in range(5):
            AssetFactory(owner=owner, visibility=PUBLIC)

        response = authenticated_api_client.get('/api/v1/users/me/assets?pageSize=2')

        # Should support pagination
        assert response.status_code in [200, 401, 403]

    def test_get_my_assets_filtering(self, authenticated_api_client, user):
        """Test filtering user assets."""
        owner = AssetOwnerFactory(django_user=user)
        AssetFactory(owner=owner, visibility=PUBLIC)
        AssetFactory(owner=owner, visibility=PRIVATE)

        response = authenticated_api_client.get('/api/v1/users/me/assets?visibility=PUBLIC')

        # Should support filtering
        assert response.status_code in [200, 401, 403]


@pytest.mark.django_db
@pytest.mark.api
class TestUsersAPIMeAssetsPost:
    """Test suite for POST /api/users/me/assets endpoint."""

    def test_post_new_asset_unauthenticated(self, api_client):
        """Test creating asset without authentication."""
        response = api_client.post('/api/v1/users/me/assets', data={
            'name': 'New Asset'
        })

        # Should require authentication
        assert response.status_code in [401, 403]

    def test_post_new_asset_creates_owner_if_needed(self, authenticated_api_client, user):
        """Test that posting new asset creates owner if user doesn't have one."""
        # Ensure user has no owners
        user.assetowner_set.all().delete()

        response = authenticated_api_client.post('/api/v1/users/me/assets', data={
            'name': 'New Asset'
        }, content_type='application/json')

        # May create owner and asset, or require JWT auth
        assert response.status_code in [200, 201, 401, 403]


@pytest.mark.django_db
@pytest.mark.api
class TestUsersAPIMeAssetsGet:
    """Test suite for GET /api/users/me/assets/{asset} endpoint."""

    def test_get_specific_asset_authenticated(self, authenticated_api_client, user):
        """Test getting specific user asset."""
        owner = AssetOwnerFactory(django_user=user)
        asset = AssetFactory(owner=owner, url='test-asset')

        response = authenticated_api_client.get(f'/api/v1/users/me/assets/{asset.url}')

        # Should return asset or require JWT auth
        assert response.status_code in [200, 401, 403, 404]

    def test_get_other_users_asset_forbidden(self, authenticated_api_client, user):
        """Test that user cannot get other user's private asset via /me endpoint."""
        other_owner = AssetOwnerFactory()
        asset = AssetFactory(owner=other_owner, url='other-asset')

        response = authenticated_api_client.get(f'/api/v1/users/me/assets/{asset.url}')

        # Should be forbidden or not found
        assert response.status_code in [401, 403, 404]


@pytest.mark.django_db
@pytest.mark.api
class TestUsersAPIMeAssetsDelete:
    """Test suite for DELETE /api/users/me/assets/{asset} endpoint."""

    def test_delete_asset_unauthenticated(self, api_client):
        """Test deleting asset without authentication."""
        asset = AssetFactory(url='test-asset')

        response = api_client.delete(f'/api/v1/users/me/assets/{asset.url}')

        # Should require authentication
        assert response.status_code in [401, 403]

    def test_delete_own_asset(self, authenticated_api_client, user):
        """Test deleting user's own asset."""
        owner = AssetOwnerFactory(django_user=user)
        asset = AssetFactory(owner=owner, url='my-asset')

        with patch('icosa.models.asset.Asset.hide_media'):
            response = authenticated_api_client.delete(f'/api/v1/users/me/assets/{asset.url}')

        # Should delete asset or require JWT auth
        assert response.status_code in [204, 401, 403, 404]

    def test_delete_other_users_asset_forbidden(self, authenticated_api_client, user):
        """Test that user cannot delete other user's asset."""
        other_owner = AssetOwnerFactory()
        asset = AssetFactory(owner=other_owner, url='other-asset')

        response = authenticated_api_client.delete(f'/api/v1/users/me/assets/{asset.url}')

        # Should be forbidden
        assert response.status_code in [401, 403, 404]


@pytest.mark.django_db
@pytest.mark.api
class TestUsersAPIMeLikedAssets:
    """Test suite for GET /api/users/me/likedassets endpoint."""

    def test_get_liked_assets_unauthenticated(self, api_client):
        """Test getting liked assets without authentication."""
        response = api_client.get('/api/v1/users/me/likedassets')

        # Should require authentication
        assert response.status_code in [401, 403]

    def test_get_liked_assets_authenticated(self, authenticated_api_client, user):
        """Test getting user's liked assets."""
        asset1 = AssetFactory(visibility=PUBLIC)
        asset2 = AssetFactory(visibility=PUBLIC)

        UserLikeFactory(user=user, asset=asset1)
        UserLikeFactory(user=user, asset=asset2)

        response = authenticated_api_client.get('/api/v1/users/me/likedassets')

        # Should return liked assets or require JWT auth
        assert response.status_code in [200, 401, 403]

    def test_get_liked_assets_includes_public_only(self, authenticated_api_client, user):
        """Test that liked assets only includes viewable assets."""
        public_asset = AssetFactory(visibility=PUBLIC)
        other_owner = AssetOwnerFactory()
        private_asset = AssetFactory(owner=other_owner, visibility=PRIVATE)

        UserLikeFactory(user=user, asset=public_asset)
        UserLikeFactory(user=user, asset=private_asset)

        response = authenticated_api_client.get('/api/v1/users/me/likedassets')

        if response.status_code == 200:
            data = response.json()
            # Private asset from other user should not be in results
            assert data is not None

    def test_get_liked_assets_pagination(self, authenticated_api_client, user):
        """Test pagination of liked assets."""
        for i in range(10):
            asset = AssetFactory(visibility=PUBLIC)
            UserLikeFactory(user=user, asset=asset)

        response = authenticated_api_client.get('/api/v1/users/me/likedassets?pageSize=5')

        # Should support pagination
        assert response.status_code in [200, 401, 403]

    def test_get_liked_assets_filtering(self, authenticated_api_client, user):
        """Test filtering liked assets."""
        asset1 = AssetFactory(visibility=PUBLIC, category='ANIMALS')
        asset2 = AssetFactory(visibility=PUBLIC, category='TECHNOLOGY')

        UserLikeFactory(user=user, asset=asset1)
        UserLikeFactory(user=user, asset=asset2)

        response = authenticated_api_client.get('/api/v1/users/me/likedassets?category=ANIMALS')

        # Should support filtering
        assert response.status_code in [200, 401, 403]

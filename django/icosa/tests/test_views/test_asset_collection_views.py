"""
Tests for asset collection view functions.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from icosa.models import AssetCollection, PUBLIC, UNLISTED, PRIVATE
from icosa.tests.fixtures.factories import (
    UserFactory,
    AssetFactory,
    AssetOwnerFactory,
    AssetCollectionFactory,
)

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.views
class TestUserAssetCollectionListView:
    """Test suite for user asset collection list view."""

    def test_collection_list_get(self, client):
        """Test GET request to collection list."""
        owner = AssetOwnerFactory()
        user = owner.django_user

        response = client.get(reverse('icosa:user_asset_collection_list', kwargs={
            'user_url': owner.url
        }))

        assert response.status_code == 200

    def test_collection_list_shows_public_collections(self, client):
        """Test that collection list shows public collections."""
        owner = AssetOwnerFactory()
        user = owner.django_user

        collection = AssetCollectionFactory(user=user, visibility=PUBLIC)

        response = client.get(reverse('icosa:user_asset_collection_list', kwargs={
            'user_url': owner.url
        }))

        assert response.status_code == 200

    def test_collection_list_shows_own_private_collections(self, authenticated_client, user):
        """Test that user sees their own private collections."""
        owner = AssetOwnerFactory(django_user=user)
        collection = AssetCollectionFactory(user=user, visibility=PRIVATE)

        response = authenticated_client.get(reverse('icosa:user_asset_collection_list', kwargs={
            'user_url': owner.url
        }))

        assert response.status_code == 200

    def test_collection_list_hides_others_private_collections(self, client):
        """Test that private collections of others are hidden."""
        other_owner = AssetOwnerFactory()
        other_user = other_owner.django_user

        private_collection = AssetCollectionFactory(user=other_user, visibility=PRIVATE)

        response = client.get(reverse('icosa:user_asset_collection_list', kwargs={
            'user_url': other_owner.url
        }))

        assert response.status_code == 200

    def test_collection_list_post_add_to_collection(self, authenticated_client, user):
        """Test POST to add asset to collection."""
        owner = AssetOwnerFactory(django_user=user)
        asset = AssetFactory(owner=owner, visibility=PUBLIC)
        collection = AssetCollectionFactory(user=user)

        response = authenticated_client.post(reverse('icosa:user_asset_collection_list', kwargs={
            'user_url': owner.url
        }), {
            'asset_url': asset.url,
            f'_add_to_collection__{collection.url}': 'true',
        })

        assert response.status_code == 200
        assert asset in collection.assets.all()

    def test_collection_list_post_remove_from_collection(self, authenticated_client, user):
        """Test POST to remove asset from collection."""
        owner = AssetOwnerFactory(django_user=user)
        asset = AssetFactory(owner=owner, visibility=PUBLIC)
        collection = AssetCollectionFactory(user=user)
        collection.assets.add(asset)

        response = authenticated_client.post(reverse('icosa:user_asset_collection_list', kwargs={
            'user_url': owner.url
        }), {
            'asset_url': asset.url,
            f'_remove_from_collection__{collection.url}': 'true',
        })

        assert response.status_code == 200
        assert asset not in collection.assets.all()

    def test_collection_list_post_create_new_collection(self, authenticated_client, user):
        """Test POST to create new collection with asset."""
        owner = AssetOwnerFactory(django_user=user)
        asset = AssetFactory(owner=owner, visibility=PUBLIC)

        response = authenticated_client.post(reverse('icosa:user_asset_collection_list', kwargs={
            'user_url': owner.url
        }), {
            'asset_url': asset.url,
            '_add_to_new_collection': 'true',
            'new-collection-name': 'My New Collection',
        })

        assert response.status_code == 200

        # Collection should be created
        collection = AssetCollection.objects.filter(name='My New Collection', user=user).first()
        assert collection is not None
        assert asset in collection.assets.all()

    def test_collection_list_post_invalid_asset(self, authenticated_client, user):
        """Test POST with invalid asset."""
        owner = AssetOwnerFactory(django_user=user)

        response = authenticated_client.post(reverse('icosa:user_asset_collection_list', kwargs={
            'user_url': owner.url
        }), {
            'asset_url': 'nonexistent',
            '_add_to_new_collection': 'true',
            'new-collection-name': 'Test',
        })

        assert response.status_code == 400

    def test_collection_list_post_no_action(self, authenticated_client, user):
        """Test POST without valid action."""
        owner = AssetOwnerFactory(django_user=user)
        asset = AssetFactory(owner=owner, visibility=PUBLIC)

        response = authenticated_client.post(reverse('icosa:user_asset_collection_list', kwargs={
            'user_url': owner.url
        }), {
            'asset_url': asset.url,
        })

        assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.views
class TestUserAssetCollectionListModalView:
    """Test suite for user asset collection list modal view."""

    def test_collection_modal_requires_login(self, client):
        """Test that collection modal requires authentication."""
        owner = AssetOwnerFactory()
        asset = AssetFactory(visibility=PUBLIC)

        response = client.get(reverse('icosa:user_asset_collection_list_modal', kwargs={
            'user_url': owner.url,
            'asset_url': asset.url,
        }))

        assert response.status_code == 302  # Redirect to login

    def test_collection_modal_loads(self, authenticated_client, user):
        """Test that collection modal loads for authenticated user."""
        owner = AssetOwnerFactory(django_user=user)
        asset = AssetFactory(owner=owner, visibility=PUBLIC)

        response = authenticated_client.get(reverse('icosa:user_asset_collection_list_modal', kwargs={
            'user_url': owner.url,
            'asset_url': asset.url,
        }))

        assert response.status_code == 200

    def test_collection_modal_shows_user_collections(self, authenticated_client, user):
        """Test that collection modal shows user's collections."""
        owner = AssetOwnerFactory(django_user=user)
        asset = AssetFactory(owner=owner, visibility=PUBLIC)
        collection = AssetCollectionFactory(user=user)

        response = authenticated_client.get(reverse('icosa:user_asset_collection_list_modal', kwargs={
            'user_url': owner.url,
            'asset_url': asset.url,
        }))

        assert response.status_code == 200
        assert 'collections' in response.context

    def test_collection_modal_marks_collections_with_asset(self, authenticated_client, user):
        """Test that collections containing the asset are marked."""
        owner = AssetOwnerFactory(django_user=user)
        asset = AssetFactory(owner=owner, visibility=PUBLIC)
        collection = AssetCollectionFactory(user=user)
        collection.assets.add(asset)

        response = authenticated_client.get(reverse('icosa:user_asset_collection_list_modal', kwargs={
            'user_url': owner.url,
            'asset_url': asset.url,
        }))

        assert response.status_code == 200

    def test_collection_modal_hides_other_users_collections(self, authenticated_client, user):
        """Test that modal doesn't show other users' collections."""
        other_owner = AssetOwnerFactory()
        owner = AssetOwnerFactory(django_user=user)
        asset = AssetFactory(owner=owner, visibility=PUBLIC)

        response = authenticated_client.get(reverse('icosa:user_asset_collection_list_modal', kwargs={
            'user_url': other_owner.url,
            'asset_url': asset.url,
        }))

        assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.views
class TestUserAssetCollectionViewView:
    """Test suite for individual collection view."""

    def test_collection_view_public(self, client):
        """Test viewing a public collection."""
        owner = AssetOwnerFactory()
        user = owner.django_user
        collection = AssetCollectionFactory(user=user, visibility=PUBLIC)

        response = client.get(reverse('icosa:user_asset_collection_view', kwargs={
            'user_url': owner.url,
            'collection_url': collection.url,
        }))

        assert response.status_code == 200

    def test_collection_view_shows_public_assets(self, client):
        """Test that collection view shows public assets."""
        owner = AssetOwnerFactory()
        user = owner.django_user
        collection = AssetCollectionFactory(user=user, visibility=PUBLIC)
        asset = AssetFactory(owner=owner, visibility=PUBLIC)
        collection.assets.add(asset)

        response = client.get(reverse('icosa:user_asset_collection_view', kwargs={
            'user_url': owner.url,
            'collection_url': collection.url,
        }))

        assert response.status_code == 200

    def test_collection_view_own_collection(self, authenticated_client, user):
        """Test viewing own collection."""
        owner = AssetOwnerFactory(django_user=user)
        collection = AssetCollectionFactory(user=user, visibility=PRIVATE)

        response = authenticated_client.get(reverse('icosa:user_asset_collection_view', kwargs={
            'user_url': owner.url,
            'collection_url': collection.url,
        }))

        assert response.status_code == 200

    def test_collection_view_private_collection_returns_404(self, client):
        """Test that private collection returns 404 for non-owners."""
        other_owner = AssetOwnerFactory()
        other_user = other_owner.django_user
        private_collection = AssetCollectionFactory(user=other_user, visibility=PRIVATE)

        response = client.get(reverse('icosa:user_asset_collection_view', kwargs={
            'user_url': other_owner.url,
            'collection_url': private_collection.url,
        }))

        assert response.status_code == 404

    def test_collection_view_unlisted_collection(self, client):
        """Test viewing an unlisted collection."""
        owner = AssetOwnerFactory()
        user = owner.django_user
        collection = AssetCollectionFactory(user=user, visibility=UNLISTED)

        response = client.get(reverse('icosa:user_asset_collection_view', kwargs={
            'user_url': owner.url,
            'collection_url': collection.url,
        }))

        assert response.status_code == 200

    def test_collection_view_pagination(self, client):
        """Test collection pagination."""
        owner = AssetOwnerFactory()
        user = owner.django_user
        collection = AssetCollectionFactory(user=user, visibility=PUBLIC)

        # Add many assets
        for i in range(30):
            asset = AssetFactory(owner=owner, visibility=PUBLIC)
            collection.assets.add(asset)

        response = client.get(reverse('icosa:user_asset_collection_view', kwargs={
            'user_url': owner.url,
            'collection_url': collection.url,
        }))

        assert response.status_code == 200

        # Test page 2
        response = client.get(
            reverse('icosa:user_asset_collection_view', kwargs={
                'user_url': owner.url,
                'collection_url': collection.url,
            }) + '?page=2'
        )

        assert response.status_code == 200

    def test_collection_view_nonexistent_collection(self, client):
        """Test viewing nonexistent collection returns 404."""
        owner = AssetOwnerFactory()

        response = client.get(reverse('icosa:user_asset_collection_view', kwargs={
            'user_url': owner.url,
            'collection_url': 'nonexistent',
        }))

        assert response.status_code == 404

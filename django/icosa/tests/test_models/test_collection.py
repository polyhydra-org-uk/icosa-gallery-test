"""
Tests for the AssetCollection and AssetCollectionAsset models.
"""
import pytest
from django.urls import reverse
from django.db import IntegrityError

from icosa.models import AssetCollection, AssetCollectionAsset
from icosa.models.common import PUBLIC, PRIVATE, UNLISTED
from icosa.tests.fixtures.factories import (
    AssetCollectionFactory,
    AssetCollectionAssetFactory,
    AssetFactory,
    UserFactory,
    AssetOwnerFactory,
    create_collection_with_assets,
)


@pytest.mark.django_db
@pytest.mark.models
class TestAssetCollectionModel:
    """Test suite for AssetCollection model."""

    def test_create_collection(self):
        """Test creating a collection with required fields."""
        collection = AssetCollectionFactory()
        assert collection.id is not None
        assert collection.name is not None
        assert collection.user is not None
        assert collection.url is not None

    def test_collection_string_representation(self):
        """Test the string representation of collection."""
        collection = AssetCollectionFactory(name='My Collection')
        assert str(collection) == 'My Collection'

    def test_collection_string_representation_no_name(self):
        """Test string representation for collection without name."""
        collection = AssetCollectionFactory(name='')
        assert str(collection) == ''

    def test_collection_url_unique(self):
        """Test that collection url must be unique."""
        url = 'unique-collection'
        AssetCollectionFactory(url=url)

        with pytest.raises(Exception):
            AssetCollectionFactory(url=url)

    def test_collection_auto_generates_url(self):
        """Test that collection auto-generates URL on save if not provided."""
        user = UserFactory()
        collection = AssetCollection(
            user=user,
            name='Test Collection'
        )
        collection.save()

        assert collection.url is not None
        assert len(collection.url) > 0

    def test_collection_visibility_public(self):
        """Test creating public collection."""
        collection = AssetCollectionFactory(visibility=PUBLIC)
        assert collection.visibility == PUBLIC

    def test_collection_visibility_private(self):
        """Test creating private collection."""
        collection = AssetCollectionFactory(visibility=PRIVATE)
        assert collection.visibility == PRIVATE

    def test_collection_visibility_unlisted(self):
        """Test creating unlisted collection."""
        collection = AssetCollectionFactory(visibility=UNLISTED)
        assert collection.visibility == UNLISTED

    def test_collection_description_field(self):
        """Test collection description field."""
        description = 'This is a test collection description'
        collection = AssetCollectionFactory(description=description)
        assert collection.description == description

    def test_collection_has_timestamps(self):
        """Test collection has create_time and update_time."""
        collection = AssetCollectionFactory()
        assert collection.create_time is not None

    def test_get_absolute_url_with_owner(self):
        """Test get_absolute_url returns correct URL when user has owner."""
        user = UserFactory()
        owner = AssetOwnerFactory(django_user=user, url='testowner')
        collection = AssetCollectionFactory(user=user, url='test-collection')

        url = collection.get_absolute_url()
        expected = reverse(
            "icosa:user_asset_collection_view",
            kwargs={
                "user_url": 'testowner',
                "collection_url": 'test-collection',
            },
        )
        assert url == expected

    def test_get_absolute_url_without_owner(self):
        """Test get_absolute_url returns None when user has no owner."""
        user = UserFactory()
        collection = AssetCollectionFactory(user=user)

        url = collection.get_absolute_url()
        assert url is None

    def test_get_thumbnail_url_with_assets(self):
        """Test get_thumbnail_url returns first asset's thumbnail."""
        collection, assets = create_collection_with_assets(num_assets=3)

        thumbnail_url = collection.get_thumbnail_url()

        # Should return the thumbnail URL from the first asset
        assert thumbnail_url is not None
        assert isinstance(thumbnail_url, str)

    def test_get_thumbnail_url_without_assets(self):
        """Test get_thumbnail_url returns default when no assets."""
        collection = AssetCollectionFactory()

        thumbnail_url = collection.get_thumbnail_url()

        # Should return default no thumbnail image
        assert 'nothumbnail.png' in thumbnail_url

    def test_collection_assets_many_to_many(self):
        """Test many-to-many relationship with assets."""
        collection = AssetCollectionFactory()
        asset1 = AssetFactory()
        asset2 = AssetFactory()

        AssetCollectionAssetFactory(collection=collection, asset=asset1, order=1)
        AssetCollectionAssetFactory(collection=collection, asset=asset2, order=2)

        assert collection.assets.count() == 2
        assert asset1 in collection.assets.all()
        assert asset2 in collection.assets.all()

    def test_collection_user_relationship(self):
        """Test collection belongs to a user."""
        user = UserFactory()
        collection = AssetCollectionFactory(user=user)

        assert collection.user == user
        assert collection in user.user_collections.all()

    def test_collection_image_field(self):
        """Test collection can have an image."""
        collection = AssetCollectionFactory(image=None)
        assert collection.image.name is None or collection.image.name == ''


@pytest.mark.django_db
@pytest.mark.models
class TestAssetCollectionAssetModel:
    """Test suite for AssetCollectionAsset model."""

    def test_create_collection_asset(self):
        """Test creating a collection asset relationship."""
        collection_asset = AssetCollectionAssetFactory()
        assert collection_asset.id is not None
        assert collection_asset.collection is not None
        assert collection_asset.asset is not None

    def test_collection_asset_string_representation(self):
        """Test string representation of collection asset."""
        asset = AssetFactory(name='Test Asset')
        collection_asset = AssetCollectionAssetFactory(
            asset=asset,
            order=5
        )

        assert str(collection_asset) == '5: Test Asset'

    def test_collection_asset_order_field(self):
        """Test order field in collection asset."""
        collection_asset = AssetCollectionAssetFactory(order=10)
        assert collection_asset.order == 10

    def test_collection_asset_ordering(self):
        """Test collection assets are ordered by order field."""
        collection = AssetCollectionFactory()
        asset1 = AssetFactory(name='Asset 1')
        asset2 = AssetFactory(name='Asset 2')
        asset3 = AssetFactory(name='Asset 3')

        # Add in non-sequential order
        AssetCollectionAssetFactory(collection=collection, asset=asset2, order=2)
        AssetCollectionAssetFactory(collection=collection, asset=asset3, order=3)
        AssetCollectionAssetFactory(collection=collection, asset=asset1, order=1)

        # Get all collection assets
        collection_assets = collection.collected_assets.all()

        # Should be ordered by order field
        assert collection_assets[0].asset == asset1
        assert collection_assets[1].asset == asset2
        assert collection_assets[2].asset == asset3

    def test_collection_asset_has_create_time(self):
        """Test collection asset has create_time."""
        collection_asset = AssetCollectionAssetFactory()
        assert collection_asset.create_time is not None

    def test_collection_asset_delete_removes_relationship(self):
        """Test deleting collection asset removes the relationship."""
        collection = AssetCollectionFactory()
        asset = AssetFactory()
        collection_asset = AssetCollectionAssetFactory(
            collection=collection,
            asset=asset
        )

        assert collection.assets.count() == 1

        collection_asset.delete()

        assert collection.assets.count() == 0

    def test_delete_collection_deletes_collection_assets(self):
        """Test deleting collection also deletes collection assets."""
        collection = AssetCollectionFactory()
        asset1 = AssetFactory()
        asset2 = AssetFactory()

        AssetCollectionAssetFactory(collection=collection, asset=asset1)
        AssetCollectionAssetFactory(collection=collection, asset=asset2)

        collection_asset_count = AssetCollectionAsset.objects.filter(
            collection=collection
        ).count()
        assert collection_asset_count == 2

        collection.delete()

        # Collection assets should be deleted (CASCADE)
        remaining = AssetCollectionAsset.objects.filter(
            collection_id=collection.id
        ).count()
        assert remaining == 0

    def test_delete_asset_deletes_collection_assets(self):
        """Test deleting asset also deletes collection assets."""
        collection = AssetCollectionFactory()
        asset = AssetFactory()
        AssetCollectionAssetFactory(collection=collection, asset=asset)

        assert collection.assets.count() == 1

        asset.delete()

        # Collection asset should be deleted (CASCADE)
        assert collection.assets.count() == 0

    def test_same_asset_multiple_collections(self):
        """Test same asset can be in multiple collections."""
        asset = AssetFactory()
        collection1 = AssetCollectionFactory()
        collection2 = AssetCollectionFactory()

        AssetCollectionAssetFactory(collection=collection1, asset=asset, order=1)
        AssetCollectionAssetFactory(collection=collection2, asset=asset, order=1)

        assert asset in collection1.assets.all()
        assert asset in collection2.assets.all()

    def test_collection_related_name(self):
        """Test collection has correct related name for assets."""
        collection = AssetCollectionFactory()
        asset = AssetFactory()
        collection_asset = AssetCollectionAssetFactory(
            collection=collection,
            asset=asset
        )

        # Access through related name
        collected = collection.collected_assets.first()
        assert collected == collection_asset

    def test_multiple_assets_in_collection_helper(self):
        """Test create_collection_with_assets helper function."""
        collection, assets = create_collection_with_assets(num_assets=5)

        assert collection.assets.count() == 5
        assert len(assets) == 5

        # Check ordering
        collected_assets = collection.collected_assets.all()
        for i, ca in enumerate(collected_assets, 1):
            assert ca.order == i

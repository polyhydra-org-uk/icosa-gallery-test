"""
Factory fixtures for creating test data using factory_boy.
"""
import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, LazyAttribute, post_generation
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from icosa.models import (
    Asset,
    AssetOwner,
    Format,
    Resource,
    Tag,
    UserLike,
    AssetCollection,
    AssetCollectionAsset,
    FormatRoleLabel,
    Oauth2Client,
    Oauth2Code,
    Oauth2Token,
)
from icosa.models.common import PUBLIC, PRIVATE, UNLISTED

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = Faker('user_name')
    email = Faker('email')
    displayname = Faker('name')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True
    is_staff = False
    is_superuser = False


class SuperUserFactory(UserFactory):
    """Factory for creating superuser instances."""

    is_staff = True
    is_superuser = True


class AssetOwnerFactory(DjangoModelFactory):
    """Factory for creating AssetOwner instances."""

    class Meta:
        model = AssetOwner

    url = Faker('user_name')
    email = Faker('email')
    displayname = Faker('name')
    migrated = False
    imported = False
    is_claimed = True
    django_user = SubFactory(UserFactory)
    disable_profile = False


class TagFactory(DjangoModelFactory):
    """Factory for creating Tag instances."""

    class Meta:
        model = Tag

    name = Faker('word')


class AssetFactory(DjangoModelFactory):
    """Factory for creating Asset instances."""

    class Meta:
        model = Asset

    url = Faker('slug')
    name = Faker('sentence', nb_words=4)
    owner = SubFactory(AssetOwnerFactory)
    description = Faker('text', max_nb_chars=200)
    visibility = PUBLIC
    curated = False
    license = 'CREATIVE_COMMONS_BY_3_0'
    category = 'ANIMALS'
    create_time = LazyAttribute(lambda _: timezone.now())
    update_time = None
    triangle_count = Faker('random_int', min=100, max=50000)
    likes = 0
    views = 0
    downloads = 0
    state = 'PUBLISHED'
    is_viewer_compatible = True
    has_gltf2 = False
    has_gltf_any = False
    has_obj = False
    has_fbx = False
    has_tilt = False
    has_blocks = False
    has_gltf1 = False
    has_vox = False

    @post_generation
    def tags(self, create, extracted, **kwargs):
        """Add tags to the asset."""
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)


class PrivateAssetFactory(AssetFactory):
    """Factory for creating private Asset instances."""
    visibility = PRIVATE


class UnlistedAssetFactory(AssetFactory):
    """Factory for creating unlisted Asset instances."""
    visibility = UNLISTED


class FormatRoleLabelFactory(DjangoModelFactory):
    """Factory for creating FormatRoleLabel instances."""

    class Meta:
        model = FormatRoleLabel

    create_time = LazyAttribute(lambda _: timezone.now())
    role_text = Faker('word')
    label = Faker('word')


class FormatFactory(DjangoModelFactory):
    """Factory for creating Format instances."""

    class Meta:
        model = Format

    asset = SubFactory(AssetFactory)
    format_type = 'GLTF2'
    triangle_count = Faker('random_int', min=100, max=50000)
    lod_hint = None
    role = 'ORIGINAL_GLTF_FORMAT'
    is_preferred_for_gallery_viewer = False
    is_preferred_for_download = True


class GLBFormatFactory(FormatFactory):
    """Factory for creating GLB Format instances."""
    format_type = 'GLB'
    role = 'GLB_FORMAT'


class OBJFormatFactory(FormatFactory):
    """Factory for creating OBJ Format instances."""
    format_type = 'OBJ'
    role = 'ORIGINAL_OBJ_FORMAT'


class FBXFormatFactory(FormatFactory):
    """Factory for creating FBX Format instances."""
    format_type = 'FBX'
    role = 'ORIGINAL_FBX_FORMAT'


class ResourceFactory(DjangoModelFactory):
    """Factory for creating Resource instances."""

    class Meta:
        model = Resource

    asset = SubFactory(AssetFactory)
    format = SubFactory(FormatFactory)
    contenttype = 'model/gltf-binary'
    file = None
    external_url = None
    hide_from_downloads = False


class UserLikeFactory(DjangoModelFactory):
    """Factory for creating UserLike instances."""

    class Meta:
        model = UserLike

    user = SubFactory(UserFactory)
    asset = SubFactory(AssetFactory)
    date_liked = LazyAttribute(lambda _: timezone.now())


class AssetCollectionFactory(DjangoModelFactory):
    """Factory for creating AssetCollection instances."""

    class Meta:
        model = AssetCollection

    user = SubFactory(UserFactory)
    name = Faker('sentence', nb_words=3)
    description = Faker('text', max_nb_chars=200)
    visibility = PUBLIC
    url = Faker('slug')


class AssetCollectionAssetFactory(DjangoModelFactory):
    """Factory for creating AssetCollectionAsset instances."""

    class Meta:
        model = AssetCollectionAsset

    collection = SubFactory(AssetCollectionFactory)
    asset = SubFactory(AssetFactory)
    order = Faker('random_int', min=1, max=100)


class Oauth2ClientFactory(DjangoModelFactory):
    """Factory for creating Oauth2Client instances."""

    class Meta:
        model = Oauth2Client

    client_id = Faker('uuid4')
    client_secret = Faker('sha256')
    client_id_issued_at = LazyAttribute(lambda _: int(timezone.now().timestamp()))
    client_secret_expires_at = 0
    client_metadata = None


class Oauth2CodeFactory(DjangoModelFactory):
    """Factory for creating Oauth2Code instances."""

    class Meta:
        model = Oauth2Code

    user_id = LazyAttribute(lambda obj: UserFactory().id)
    code = Faker('sha256')
    client_id = Faker('uuid4')
    redirect_uri = Faker('url')
    response_type = 'code'
    auth_time = LazyAttribute(lambda _: int(timezone.now().timestamp()))
    code_challenge = None
    code_challenge_method = None
    scope = 'read write'
    nonce = None


class Oauth2TokenFactory(DjangoModelFactory):
    """Factory for creating Oauth2Token instances."""

    class Meta:
        model = Oauth2Token

    user_id = LazyAttribute(lambda obj: UserFactory().id)
    client_id = Faker('uuid4')
    token_type = 'Bearer'
    access_token = Faker('sha256')
    refresh_token = Faker('sha256')
    scope = 'read write'
    issued_at = LazyAttribute(lambda _: int(timezone.now().timestamp()))
    access_token_revoked_at = 0
    refresh_token_revoked_at = 0
    expires_in = 3600


# Helper functions for creating complex test data

def create_asset_with_formats(owner=None, num_formats=2, **kwargs):
    """Create an asset with multiple formats and resources."""
    if owner is None:
        owner = AssetOwnerFactory()

    asset = AssetFactory(owner=owner, **kwargs)
    formats = []

    for i in range(num_formats):
        if i == 0:
            format_instance = GLBFormatFactory(asset=asset)
        elif i == 1:
            format_instance = OBJFormatFactory(asset=asset)
        else:
            format_instance = FormatFactory(asset=asset)

        # Create a resource for each format
        ResourceFactory(asset=asset, format=format_instance)
        formats.append(format_instance)

    # Update denormalized fields
    asset.denorm_format_types()
    asset.save()

    return asset, formats


def create_asset_with_likes(owner=None, num_likes=5, **kwargs):
    """Create an asset with multiple user likes."""
    if owner is None:
        owner = AssetOwnerFactory()

    asset = AssetFactory(owner=owner, **kwargs)
    likes = []

    for _ in range(num_likes):
        user = UserFactory()
        like = UserLikeFactory(user=user, asset=asset)
        likes.append(like)

    asset.likes = num_likes
    asset.save()

    return asset, likes


def create_collection_with_assets(user=None, num_assets=5, **kwargs):
    """Create a collection with multiple assets."""
    if user is None:
        owner = AssetOwnerFactory()
        user = owner.django_user

    collection = AssetCollectionFactory(user=user, **kwargs)
    assets = []

    for i in range(num_assets):
        # Create assets owned by an asset owner associated with the user
        asset_owner = user.assetowner_set.first()
        if not asset_owner:
            asset_owner = AssetOwnerFactory(django_user=user)
        asset = AssetFactory(owner=asset_owner)
        AssetCollectionAssetFactory(
            collection=collection,
            asset=asset,
            order=i + 1
        )
        assets.append(asset)

    return collection, assets

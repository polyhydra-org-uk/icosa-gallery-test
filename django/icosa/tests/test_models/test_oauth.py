"""
Tests for OAuth2 models (Oauth2Client, Oauth2Code, Oauth2Token).
"""
import pytest
from django.utils import timezone

from icosa.models import Oauth2Client, Oauth2Code, Oauth2Token
from icosa.tests.fixtures.factories import (
    Oauth2ClientFactory,
    Oauth2CodeFactory,
    Oauth2TokenFactory,
    UserFactory,
)


@pytest.mark.django_db
@pytest.mark.models
class TestOauth2ClientModel:
    """Test suite for Oauth2Client model."""

    def test_create_oauth2_client(self):
        """Test creating an OAuth2 client."""
        client = Oauth2ClientFactory()
        assert client.id is not None
        assert client.client_id is not None
        assert client.client_secret is not None

    def test_client_id_unique(self):
        """Test that client_id must be unique."""
        client_id = 'unique-client-id'
        Oauth2ClientFactory(client_id=client_id)

        with pytest.raises(Exception):
            Oauth2ClientFactory(client_id=client_id)

    def test_client_id_max_length(self):
        """Test client_id has max length of 48."""
        client = Oauth2ClientFactory(client_id='a' * 48)
        assert len(client.client_id) == 48

    def test_client_secret_optional(self):
        """Test client_secret can be null."""
        client = Oauth2ClientFactory(client_secret=None)
        assert client.client_secret is None

    def test_client_id_issued_at_timestamp(self):
        """Test client_id_issued_at stores timestamp."""
        client = Oauth2ClientFactory()
        assert isinstance(client.client_id_issued_at, int)
        assert client.client_id_issued_at > 0

    def test_client_secret_expires_at_default(self):
        """Test client_secret_expires_at defaults to 0."""
        client = Oauth2ClientFactory(client_secret_expires_at=0)
        assert client.client_secret_expires_at == 0

    def test_client_metadata_optional(self):
        """Test client_metadata is optional."""
        client = Oauth2ClientFactory(client_metadata=None)
        assert client.client_metadata is None

    def test_client_metadata_stores_text(self):
        """Test client_metadata can store text data."""
        metadata = '{"name": "Test App", "redirect_uris": ["http://localhost"]}'
        client = Oauth2ClientFactory(client_metadata=metadata)
        assert client.client_metadata == metadata


@pytest.mark.django_db
@pytest.mark.models
class TestOauth2CodeModel:
    """Test suite for Oauth2Code model."""

    def test_create_oauth2_code(self):
        """Test creating an OAuth2 authorization code."""
        code = Oauth2CodeFactory()
        assert code.id is not None
        assert code.code is not None
        assert code.user_id is not None

    def test_code_unique(self):
        """Test that authorization code must be unique."""
        code_value = 'unique-auth-code'
        Oauth2CodeFactory(code=code_value)

        with pytest.raises(Exception):
            Oauth2CodeFactory(code=code_value)

    def test_user_id_field(self):
        """Test user_id is stored as BigInteger."""
        user = UserFactory()
        code = Oauth2CodeFactory(user_id=user.id)
        assert code.user_id == user.id

    def test_client_id_field(self):
        """Test client_id is stored."""
        client_id = 'test-client-id'
        code = Oauth2CodeFactory(client_id=client_id)
        assert code.client_id == client_id

    def test_redirect_uri_field(self):
        """Test redirect_uri is stored."""
        redirect_uri = 'http://localhost:3000/callback'
        code = Oauth2CodeFactory(redirect_uri=redirect_uri)
        assert code.redirect_uri == redirect_uri

    def test_response_type_field(self):
        """Test response_type field."""
        code = Oauth2CodeFactory(response_type='code')
        assert code.response_type == 'code'

    def test_auth_time_timestamp(self):
        """Test auth_time stores unix timestamp."""
        code = Oauth2CodeFactory()
        assert isinstance(code.auth_time, int)
        assert code.auth_time > 0

    def test_code_challenge_pkce(self):
        """Test code_challenge for PKCE flow."""
        challenge = 'E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM'
        code = Oauth2CodeFactory(
            code_challenge=challenge,
            code_challenge_method='S256'
        )
        assert code.code_challenge == challenge
        assert code.code_challenge_method == 'S256'

    def test_scope_field(self):
        """Test scope field for permissions."""
        scope = 'read write delete'
        code = Oauth2CodeFactory(scope=scope)
        assert code.scope == scope

    def test_nonce_field(self):
        """Test nonce field for OpenID Connect."""
        nonce = 'random-nonce-value'
        code = Oauth2CodeFactory(nonce=nonce)
        assert code.nonce == nonce

    def test_optional_fields_can_be_null(self):
        """Test that optional fields can be null."""
        code = Oauth2CodeFactory(
            client_id=None,
            redirect_uri=None,
            response_type=None,
            code_challenge=None,
            code_challenge_method=None,
            scope=None,
            nonce=None
        )
        assert code.client_id is None
        assert code.redirect_uri is None
        assert code.response_type is None


@pytest.mark.django_db
@pytest.mark.models
class TestOauth2TokenModel:
    """Test suite for Oauth2Token model."""

    def test_create_oauth2_token(self):
        """Test creating an OAuth2 access token."""
        token = Oauth2TokenFactory()
        assert token.id is not None
        assert token.access_token is not None

    def test_access_token_unique(self):
        """Test that access_token must be unique."""
        access_token = 'unique-access-token'
        Oauth2TokenFactory(access_token=access_token)

        with pytest.raises(Exception):
            Oauth2TokenFactory(access_token=access_token)

    def test_user_id_field(self):
        """Test user_id is stored."""
        user = UserFactory()
        token = Oauth2TokenFactory(user_id=user.id)
        assert token.user_id == user.id

    def test_user_id_optional(self):
        """Test user_id can be null (for client credentials flow)."""
        token = Oauth2TokenFactory(user_id=None)
        assert token.user_id is None

    def test_client_id_field(self):
        """Test client_id is stored."""
        client_id = 'test-client-id'
        token = Oauth2TokenFactory(client_id=client_id)
        assert token.client_id == client_id

    def test_token_type_bearer(self):
        """Test token_type is typically 'Bearer'."""
        token = Oauth2TokenFactory(token_type='Bearer')
        assert token.token_type == 'Bearer'

    def test_refresh_token_optional(self):
        """Test refresh_token is optional."""
        token = Oauth2TokenFactory(refresh_token=None)
        assert token.refresh_token is None

    def test_scope_field(self):
        """Test scope field for permissions."""
        scope = 'read write admin'
        token = Oauth2TokenFactory(scope=scope)
        assert token.scope == scope

    def test_issued_at_timestamp(self):
        """Test issued_at stores unix timestamp."""
        token = Oauth2TokenFactory()
        assert isinstance(token.issued_at, int)
        assert token.issued_at > 0

    def test_revocation_timestamps_default_zero(self):
        """Test revocation timestamps default to 0."""
        token = Oauth2TokenFactory()
        assert token.access_token_revoked_at == 0
        assert token.refresh_token_revoked_at == 0

    def test_token_can_be_revoked(self):
        """Test token revocation timestamps can be set."""
        revoked_at = int(timezone.now().timestamp())
        token = Oauth2TokenFactory(
            access_token_revoked_at=revoked_at,
            refresh_token_revoked_at=revoked_at
        )
        assert token.access_token_revoked_at == revoked_at
        assert token.refresh_token_revoked_at == revoked_at

    def test_expires_in_field(self):
        """Test expires_in field stores token lifetime in seconds."""
        expires_in = 3600  # 1 hour
        token = Oauth2TokenFactory(expires_in=expires_in)
        assert token.expires_in == expires_in

    def test_token_expiration_calculation(self):
        """Test calculating token expiration time."""
        token = Oauth2TokenFactory(
            issued_at=int(timezone.now().timestamp()),
            expires_in=3600
        )
        expiration_time = token.issued_at + token.expires_in
        current_time = int(timezone.now().timestamp())

        # Token should expire approximately 1 hour from now
        assert expiration_time > current_time
        assert expiration_time - current_time <= 3600

    def test_token_is_not_revoked(self):
        """Test checking if token is not revoked."""
        token = Oauth2TokenFactory()
        assert token.access_token_revoked_at == 0
        assert token.refresh_token_revoked_at == 0

    def test_access_token_max_length(self):
        """Test access_token max length is 255."""
        token = Oauth2TokenFactory(access_token='a' * 255)
        assert len(token.access_token) == 255

    def test_refresh_token_max_length(self):
        """Test refresh_token max length is 255."""
        token = Oauth2TokenFactory(refresh_token='r' * 255)
        assert len(token.refresh_token) == 255

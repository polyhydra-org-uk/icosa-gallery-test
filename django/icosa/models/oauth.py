from django.db import models
from django.utils.translation import gettext_lazy as _


class Oauth2Client(models.Model):
    id = models.BigAutoField(primary_key=True)
    client_id = models.CharField(_("Client ID"), max_length=48, unique=True)
    client_secret = models.CharField(_("Client Secret"), max_length=120, blank=True, null=True)
    client_id_issued_at = models.IntegerField(_("Client ID Issued At"), default=0)
    client_secret_expires_at = models.IntegerField(_("Client Secret Expires At"), default=0)
    client_metadata = models.TextField(_("Client Metadata"), blank=True, null=True)

    class Meta:
        verbose_name = _("OAuth2 Client")
        verbose_name_plural = _("OAuth2 Clients")


class Oauth2Code(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField(_("User ID"))
    code = models.CharField(_("Code"), max_length=120, unique=True)
    client_id = models.CharField(_("Client ID"), max_length=48, blank=True, null=True)
    redirect_uri = models.TextField(_("Redirect URI"), blank=True, null=True)
    response_type = models.TextField(_("Response Type"), blank=True, null=True)
    auth_time = models.IntegerField(_("Auth Time"))
    code_challenge = models.TextField(_("Code Challenge"), blank=True, null=True)
    code_challenge_method = models.CharField(_("Code Challenge Method"), max_length=48, blank=True, null=True)
    scope = models.TextField(_("Scope"), blank=True, null=True)
    nonce = models.TextField(_("Nonce"), blank=True, null=True)

    class Meta:
        verbose_name = _("OAuth2 Authorization Code")
        verbose_name_plural = _("OAuth2 Authorization Codes")


class Oauth2Token(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField(_("User ID"), blank=True, null=True)
    client_id = models.CharField(_("Client ID"), max_length=48, blank=True, null=True)
    token_type = models.CharField(_("Token Type"), max_length=40, blank=True, null=True)
    access_token = models.CharField(_("Access Token"), max_length=255, unique=True)
    refresh_token = models.CharField(_("Refresh Token"), max_length=255, blank=True, null=True)
    scope = models.TextField(_("Scope"), blank=True, null=True)
    issued_at = models.IntegerField(_("Issued At"))
    access_token_revoked_at = models.IntegerField(_("Access Token Revoked At"), default=0)
    refresh_token_revoked_at = models.IntegerField(_("Refresh Token Revoked At"), default=0)
    expires_in = models.IntegerField(_("Expires In"), default=0)

    class Meta:
        verbose_name = _("OAuth2 Token")
        verbose_name_plural = _("OAuth2 Tokens")

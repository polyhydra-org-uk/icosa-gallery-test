from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class DeviceCode(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        help_text=_("User associated with this device code"),
    )
    devicecode = models.CharField(_("Device Code"), max_length=6, help_text=_("Short code for device authentication"))
    expiry = models.DateTimeField(_("Expiry"), help_text=_("When this code expires"))

    class Meta:
        verbose_name = _("Device Code")
        verbose_name_plural = _("Device Codes")

    def __str__(self):
        return f"{self.devicecode}: {self.expiry}"

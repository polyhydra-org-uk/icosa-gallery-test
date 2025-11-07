from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .asset import Asset


class UserLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="likedassets",
        help_text=_("User who liked the asset"),
    )
    asset = models.ForeignKey(
        Asset,
        verbose_name=_("Asset"),
        on_delete=models.CASCADE,
        help_text=_("Asset that was liked"),
    )
    date_liked = models.DateTimeField(_("Date Liked"), auto_now_add=True, help_text=_("When the user liked this asset"))

    class Meta:
        verbose_name = _("User Like")
        verbose_name_plural = _("User Likes")

    def __str__(self):
        date_str = self.date_liked.strftime("%d/%m/%Y %H:%M:%S %Z")
        return f"{self.user.displayname} -> {self.asset.name} @ {date_str}"

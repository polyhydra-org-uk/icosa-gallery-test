from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    name = models.CharField(_("Name"), max_length=255, unique=True, help_text=_("Tag name for categorizing assets"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = [
            "name",
        ]

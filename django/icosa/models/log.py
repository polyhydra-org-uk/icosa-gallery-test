from b2sdk._internal.exception import FileNotHidden, FileNotPresent

from django.db import models
from django.utils.translation import gettext_lazy as _
from icosa.helpers.storage import get_b2_bucket

from .common import FILENAME_MAX_LENGTH


class HiddenMediaFileLog(models.Model):
    original_asset_id = models.BigIntegerField(_("Original Asset ID"), help_text=_("ID of the asset this file belonged to"))
    file_name = models.CharField(_("File Name"), max_length=FILENAME_MAX_LENGTH, help_text=_("Name of the hidden file"))
    deleted_from_source = models.BooleanField(
        _("Deleted from Source"),
        default=False,
        help_text=_("Whether the file has been permanently deleted from storage"),
    )

    class Meta:
        verbose_name = _("Hidden Media File Log")
        verbose_name_plural = _("Hidden Media File Logs")

    def unhide(self):
        bucket = get_b2_bucket()
        try:
            bucket.unhide_file(self.file_name)
        except FileNotPresent:
            print("File not present in storage, marking as deleted")
            self.deleted_from_source = True
            self.save()
        except FileNotHidden:
            print("File already not hidden, nothing to do.")

    def __str__(self):
        return f"{self.original_asset_id}: {self.file_name}"


class BulkSaveLog(models.Model):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    KILLED = "KILLED"
    RESUMED = "RESUMED"

    BULK_SAVE_STATUS_CHOICES = [
        (SUCCEEDED, _("Succeeded")),
        (FAILED, _("Failed")),
        (KILLED, _("Killed")),
        (RESUMED, _("Resumed")),
    ]
    create_time = models.DateTimeField(_("Created"), auto_now_add=True)
    update_time = models.DateTimeField(_("Last Updated"), auto_now=True)
    finish_time = models.DateTimeField(_("Finished"), null=True, blank=True, help_text=_("When the bulk save operation finished"))
    finish_status = models.CharField(
        _("Finish Status"),
        max_length=9,
        null=True,
        blank=True,
        choices=BULK_SAVE_STATUS_CHOICES,
        help_text=_("Final status of the bulk save operation"),
    )
    kill_sig = models.BooleanField(_("Kill Signal"), default=False, help_text=_("Whether a kill signal was sent to stop this operation"))
    last_id = models.BigIntegerField(_("Last ID"), null=True, blank=True, help_text=_("ID of the last processed item"))

    class Meta:
        verbose_name = _("Bulk Save Log")
        verbose_name_plural = _("Bulk Save Logs")

from django.db import models
from django.utils.translation import gettext_lazy as _


class Room(models.Model):
    """ Represents a physical room of the Escape Room.
    """
    name = models.CharField(_("Name"), max_length=50)
    is_active = models.BooleanField(_("Active"), default=False)
    description = models.TextField(_("Description"), blank=True, null=True)
    # photo = models.ImageField(_("Image"), upload_to='uploads/rooms', height_field=None, width_field=None, max_length=None, null=True, blank=True)
    photo_alt = models.CharField(_("Alt text"), max_length=128, null=True, blank=True)
    theme_colour = models.CharField(_("Colour Hexagesimal"), max_length=6, default="999999")

    def get_page(self):
        if self.room_page:
            return self.room_page.first()


    def __str__(self):
        return self.name

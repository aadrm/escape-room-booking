"""
Singleton Abstract Model
"""
import re
from django.db.models.signals import post_migrate, pre_migrate
from django.db import models
from django.dispatch import receiver


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def load(cls):
        instance, _ = cls.objects.get_or_create(pk=1)
        return instance

    def delete(self, *args, **kwargs):
        # Override delete method to prevent deletion
        pass

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        class_name = self.__class__.__name__
        # Add spaces between words in class name
        display_name = ' '.join(
            word.capitalize() for word in re.findall(r'[A-Za-z][a-z]*', class_name)
        )
        return display_name

from django.db import models

class Client(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(
        max_length=32,
        blank=True,
        help_text="WhatsApp phone in international format (digits only preferred), e.g. 15551234567",
    )
    messenger_username = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

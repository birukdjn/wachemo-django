from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from student.models import Message

class MessagingService:
    @staticmethod
    def send_direct_message(sender_user: User, recipient_user: User, subject: str, body: str) -> Message:
        """
        Sends direct message with server-controlled sender attribution.
        """
        if not sender_user or not sender_user.is_authenticated:
            raise ValidationError("Sender must be an authenticated user.")
            
        if not recipient_user:
            raise ValidationError("Recipient is required.")

        return Message.objects.create(
            sender=sender_user,
            recipient=recipient_user,
            subject=subject.strip(),
            body=body.strip()
        )

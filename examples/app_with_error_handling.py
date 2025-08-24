from gmail_sender import send_email, GmailSendError

try:
    send_email(
        fromaddr="you@gmail.com",
        toaddr="recipient@example.com",
        subject="Hi",
        body="Test",
    )
except GmailSendError as e:
    print("Failed to send:", e)\n
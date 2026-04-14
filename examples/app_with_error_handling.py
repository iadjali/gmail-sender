from gmail_sender import GmailSendError, send_email

try:
    send_email(
        fromaddr="you@gmail.com",
        toaddr="recipient@example.com",
        subject="Hi",
        body="Test",
    )
except GmailSendError as e:
    print("Failed to send:", e)

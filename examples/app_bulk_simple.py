from gmail_sender import send_email

recipients = ["a@example.com", "b@example.com", "c@example.com"]

for r in recipients:
    send_email(
        fromaddr="you@gmail.com",
        toaddr=r,
        subject="Hello",
        body=f"Hi {r}!",
    )

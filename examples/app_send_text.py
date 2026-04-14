from gmail_sender import send_email

send_email(
    fromaddr="you@gmail.com",
    toaddr="recipient@example.com",
    subject="Hello",
    body="Hi from my app!",
    html=False,
)

from gmail_sender import send_email, get_service

# Reuse a single service instance for many sends (more efficient for batches)
service = get_service()

recipients = ["a@example.com", "b@example.com", "c@example.com"]
for r in recipients:
    send_email(
        fromaddr="you@gmail.com",
        toaddr=r,
        subject="Hello (reused service)",
        body=f"Hi {r}!",
        service=service,  # <- reuse the same Gmail API client
    )

from gmail_sender import send_email

def notify_new_user(user_email: str) -> None:
    html_body = f"""
    <h2>Welcome!</h2>
    <p>Hi {user_email}, thanks for signing up.</p>
    """
    send_email(
        fromaddr="you@gmail.com",
        toaddr=user_email,
        subject="Welcome 🎉",
        body=html_body,
        html=True,
    )

if __name__ == "__main__":
    notify_new_user("new.user@example.com")

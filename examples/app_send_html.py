from gmail_sender import send_email

html_body = """
<h1 style="margin:0">Daily Update</h1>
<p>All systems green ✅</p>
"""

send_email(
    fromaddr="you@gmail.com",
    toaddr="recipient@example.com",
    subject="Daily Update",
    body=html_body,
    html=True,
)

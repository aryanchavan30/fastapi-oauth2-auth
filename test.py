import smtplib
from email.mime.text import MIMEText

# --- IMPORTANT: FILL THESE IN ---
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "aryanchavansony@gmail.com"
SMTP_PASSWORD = "tieurzpbpkgfzcge" # Your App Password
TO_EMAIL = "aryanchavansony@gmail.com" # Send a test to yourself

# --- Test Email Content ---
subject = "SMTP Test from Python Script"
body = "If you received this, your SMTP credentials and connection are working!"

try:
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = TO_EMAIL

    print("Connecting to server...")
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    print("Logging in...")
    server.login(SMTP_USER, SMTP_PASSWORD)
    print("Sending email...")
    server.send_message(msg)
    server.quit()
    print("Test email sent successfully!")

except Exception as e:
    print("Failed to send test email.")
    print(f"Error: {e}")
"""
Kindle Email Sender
Sends HTML documents to Kindle via Amazon's Personal Document Service
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KindleSender:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        """
        Initialize Kindle sender

        Args:
            smtp_server: SMTP server address (e.g., smtp.gmail.com)
            smtp_port: SMTP port (usually 587 for TLS)
            sender_email: Your email address (must be approved in Amazon account)
            sender_password: Email password (use App Password for Gmail)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_to_kindle(self, kindle_email, html_file_path, subject=None):
        """
        Send HTML file to Kindle email address

        Args:
            kindle_email: Kindle email address (e.g., yourname@kindle.com)
            html_file_path: Path to HTML file to send
            subject: Email subject (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Default subject
            if subject is None:
                today = datetime.now().strftime('%Y-%m-%d')
                subject = f'Daily News Digest - {today}'

            logger.info(f"Sending {html_file_path} to {kindle_email}")

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = kindle_email
            msg['Subject'] = subject

            # Add body text
            body = "Your daily news digest is attached."
            msg.attach(MIMEText(body, 'plain'))

            # Attach HTML file
            if not os.path.exists(html_file_path):
                logger.error(f"File not found: {html_file_path}")
                return False

            with open(html_file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())

            encoders.encode_base64(part)

            # Get filename from path
            filename = os.path.basename(html_file_path)

            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}',
            )

            msg.attach(part)

            # Connect to SMTP server and send
            logger.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}")

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable TLS
                server.login(self.sender_email, self.sender_password)
                text = msg.as_string()
                server.sendmail(self.sender_email, kindle_email, text)

            logger.info(f"Successfully sent email to {kindle_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {e}")
            logger.error("If using Gmail, make sure you're using an App Password, not your regular password")
            logger.error("Generate App Password at: https://myaccount.google.com/apppasswords")
            return False

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
            return False

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def send_html_content(self, kindle_email, html_content, filename=None, subject=None):
        """
        Send HTML content directly to Kindle (creates temporary file)

        Args:
            kindle_email: Kindle email address
            html_content: HTML content as string
            filename: Name for the temporary file (optional)
            subject: Email subject (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create temporary file
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'news_{timestamp}.html'

            temp_file = f'/tmp/{filename}'

            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Send the file
            result = self.send_to_kindle(kindle_email, temp_file, subject)

            # Clean up temporary file
            try:
                os.remove(temp_file)
                logger.info(f"Cleaned up temporary file: {temp_file}")
            except:
                pass

            return result

        except Exception as e:
            logger.error(f"Error sending HTML content: {e}")
            return False


def test_connection(smtp_server, smtp_port, sender_email, sender_password):
    """
    Test SMTP connection and authentication

    Returns:
        bool: True if connection successful
    """
    try:
        logger.info(f"Testing connection to {smtp_server}:{smtp_port}")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)

        logger.info("Connection test successful!")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("Authentication failed. Check your email and password.")
        logger.error("If using Gmail, use an App Password: https://myaccount.google.com/apppasswords")
        return False

    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the sender
    import yaml

    try:
        with open('../config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        # Test connection
        print("\n=== Testing SMTP Connection ===")
        success = test_connection(
            config['email']['smtp_server'],
            config['email']['smtp_port'],
            config['email']['sender_email'],
            config['email']['sender_password']
        )

        if success:
            print("\n=== Connection successful! ===")

            # Test sending
            response = input("\nDo you want to send a test email to your Kindle? (y/n): ")
            if response.lower() == 'y':
                sender = KindleSender(
                    config['email']['smtp_server'],
                    config['email']['smtp_port'],
                    config['email']['sender_email'],
                    config['email']['sender_password']
                )

                test_html = """
                <!DOCTYPE html>
                <html>
                <head><title>Test</title></head>
                <body>
                    <h1>Test Email</h1>
                    <p>This is a test email from Kindle News Delivery system.</p>
                </body>
                </html>
                """

                result = sender.send_html_content(
                    config['kindle']['email'],
                    test_html,
                    subject="Test Email from Kindle News Delivery"
                )

                if result:
                    print("\n=== Test email sent successfully! ===")
                    print("Check your Kindle or Kindle app to see if it arrives.")
                else:
                    print("\n=== Failed to send test email ===")

    except FileNotFoundError:
        print("Please create config.yaml from config.example.yaml")
    except KeyError as e:
        print(f"Missing configuration key: {e}")
    except Exception as e:
        print(f"Error: {e}")

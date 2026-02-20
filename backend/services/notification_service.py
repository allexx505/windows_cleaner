"""
Notifications: Windows toast and email. Used by monitor when thresholds
or cleanup rules trigger alerts.
"""
from backend.core.config import load_config


def send_windows_toast(title: str, message: str) -> None:
    """Show Windows notification (toast). No-op if disabled or import fails."""
    try:
        cfg = load_config()
        if not getattr(cfg.notification, "use_windows_toast", True):
            return
        try:
            from desktop_notifier.sync import DesktopNotifierSync
            notifier = DesktopNotifierSync(app_name="Windows Cleaner")
            notifier.send(title=title, message=message)
        except ImportError:
            from desktop_notifier import DesktopNotifier
            import asyncio
            notifier = DesktopNotifier(app_name="Windows Cleaner")
            asyncio.run(notifier.send(title=title, message=message))
    except Exception:
        pass


def send_email(subject: str, body: str) -> None:
    """Send email to configured address. No-op if disabled or config missing."""
    try:
        cfg = load_config()
        n = cfg.notification
        if not getattr(n, "email_enabled", False) or not getattr(n, "notify_email_to", ""):
            return
        to_addr = n.notify_email_to
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = getattr(n, "smtp_user", "") or "windows-cleaner@local"
        msg["To"] = to_addr
        msg.attach(MIMEText(body, "plain", "utf-8"))
        port = getattr(n, "smtp_port", 465)
        use_tls = getattr(n, "smtp_use_tls", True)
        with smtplib.SMTP_SSL(n.smtp_host, port) if use_tls else smtplib.SMTP(n.smtp_host, port) as s:
            if not use_tls:
                s.starttls()
            s.login(n.smtp_user, n.smtp_password)
            s.send_message(msg)
    except Exception:
        pass


def notify_alert(title: str, message: str) -> None:
    """Send both Windows toast and email (if configured)."""
    send_windows_toast(title, message)
    send_email(title, message)

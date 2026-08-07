from datetime import datetime, timezone
from backend import celery, mail, db
from backend.models import Application, Student, Job, Company
from flask_mail import Message
import calendar


@celery.task(name='backend.tasks.reports.send_monthly_report')
def send_monthly_report():
    now = datetime.now(timezone.utc)
    # Get last month's range
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_end = first_day
    last_month_start = (first_day.replace(month=first_day.month - 1)
                        if first_day.month > 1
                        else first_day.replace(year=first_day.year - 1, month=12))

    apps = Application.query.filter(
        Application.application_date >= last_month_start,
        Application.application_date < last_month_end
    ).all()

    total_drives = Job.query.filter(
        Job.created_at >= last_month_start,
        Job.created_at < last_month_end
    ).count()

    total_applied = len(apps)
    total_selected = sum(1 for a in apps if a.status in ['selected', 'placed'])

    report_body = f"""
Monthly Placement Activity Report
Period: {last_month_start.strftime('%B %Y')}

Total Drives Conducted: {total_drives}
Total Applications: {total_applied}
Total Students Selected: {total_selected}

Generated on: {now.strftime('%Y-%m-%d %H:%M')}
Placement Portal System
    """

    from backend import create_app
    app = create_app()
    admin_email = app.config['ADMIN_EMAIL']

    msg = Message(
        subject=f"Monthly Placement Report - {last_month_start.strftime('%B %Y')}",
        recipients=[admin_email],
        body=report_body
    )
    mail.send(msg)

    return f"Monthly report sent to {admin_email}"
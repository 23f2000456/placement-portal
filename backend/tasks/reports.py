from datetime import datetime, timezone
from backend import celery, mail, db
from backend.models import Application, Job
from flask_mail import Message


@celery.task(name='backend.tasks.reports.send_monthly_report')
def send_monthly_report():
    now = datetime.now(timezone.utc)

    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if first_day.month == 1:
        last_month_start = first_day.replace(year=first_day.year - 1, month=12)
    else:
        last_month_start = first_day.replace(month=first_day.month - 1)
    last_month_end = first_day

    all_apps = Application.query.all()
    all_drives = Job.query.count()
    all_selected = sum(1 for a in all_apps if a.status in ['selected', 'placed'])

    monthly_apps = Application.query.filter(
        Application.application_date >= last_month_start,
        Application.application_date < last_month_end
    ).all()
    monthly_drives = Job.query.filter(
        Job.created_at >= last_month_start,
        Job.created_at < last_month_end
    ).count()
    monthly_selected = sum(1 for a in monthly_apps if a.status in ['selected', 'placed'])

    from backend import create_app
    app = create_app()
    admin_email = app.config['ADMIN_EMAIL']

    report_body = f"""
Placement Portal — Activity Report
Generated: {now.strftime('%Y-%m-%d %H:%M')} IST

═══════════════════════════════════
LAST MONTH ({last_month_start.strftime('%B %Y')})
═══════════════════════════════════
Drives Conducted: {monthly_drives}
Applications Received: {len(monthly_apps)}
Students Selected: {monthly_selected}

═══════════════════════════════════
ALL TIME SUMMARY
═══════════════════════════════════
Total Drives: {all_drives}
Total Applications: {len(all_apps)}
Total Selected: {all_selected}

Placement Portal System
    """

    msg = Message(
        subject=f"Placement Activity Report - {now.strftime('%B %Y')}",
        recipients=[admin_email],
        body=report_body
    )
    mail.send(msg)

    return f"Report sent to {admin_email}"

from datetime import datetime, timedelta, timezone
from backend import celery, mail
from backend.models import Job, Application, Student, User
from flask_mail import Message


@celery.task(name='backend.tasks.reminders.send_interview_reminders')
def send_interview_reminders():
    now = datetime.now(timezone.utc)
    tomorrow = now + timedelta(days=1)
    start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Jobs with deadline tomorrow (scheduled daily run)
    upcoming_jobs = Job.query.filter(
        Job.application_deadline >= start,
        Job.application_deadline <= end,
        Job.status == 'approved'
    ).all()

    # For manual trigger — use all future jobs if none due tomorrow
    if not upcoming_jobs:
        upcoming_jobs = Job.query.filter(
            Job.application_deadline >= now,
            Job.status == 'approved'
        ).all()

    all_students = Student.query.filter_by(is_blacklisted=False).all()
    sent = 0

    # Send deadline reminders to all eligible students
    for job in upcoming_jobs:
        applied_student_ids = [a.student_id for a in job.applications]

        for student in all_students:
            user = User.query.get(student.user_id)

            # Send to ALL students — both applied and not applied
            # Applied students get a "your application is active" reminder
            # Non-applied students get a "don't miss out" reminder
            if student.id in applied_student_ids:
                subject = f"Reminder: Your application deadline is approaching — {job.job_title}"
                body = f"""
Hi {student.full_name},

This is a reminder that the application deadline for a drive you applied to is approaching!

Company: {job.company.company_name}
Position: {job.job_title}
Deadline: {job.application_deadline.strftime('%Y-%m-%d')}

You have already applied — stay tuned for updates on your application status.

Best regards,
Placement Portal Team
                """
            else:
                subject = f"Don't miss out! Application deadline approaching — {job.job_title}"
                body = f"""
Hi {student.full_name},

You haven't applied to this placement drive yet and the deadline is approaching!

Company: {job.company.company_name}
Position: {job.job_title}
Deadline: {job.application_deadline.strftime('%Y-%m-%d')}

Apply now on the Placement Portal before it's too late!

Best regards,
Placement Portal Team
                """

            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body
            )
            mail.send(msg)
            sent += 1

    return f"Sent {sent} deadline reminders"

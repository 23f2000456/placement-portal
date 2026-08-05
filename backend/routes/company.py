from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from backend import db
from backend.models import Company, Job, Application, Student
from backend.utils import role_required
from datetime import datetime, timezone

company_bp = Blueprint('company', __name__, url_prefix='/api/company')


def get_current_company():
    user_id = get_jwt_identity()
    return Company.query.filter_by(user_id=int(user_id)).first()


@company_bp.route('/dashboard', methods=['GET'])
@role_required('company')
def dashboard():
    company = get_current_company()
    jobs = Job.query.filter_by(company_id=company.id).all()
    total_applications = sum(len(j.applications) for j in jobs)
    shortlisted = Application.query.join(Job).filter(
        Job.company_id == company.id,
        Application.status == 'shortlisted'
    ).count()
    return jsonify({
        "company_name": company.company_name,
        "total_job_postings": len(jobs),
        "total_applications": total_applications,
        "shortlisted_candidates": shortlisted
    })


@company_bp.route('/jobs', methods=['GET'])
@role_required('company')
def list_jobs():
    company = get_current_company()
    jobs = Job.query.filter_by(company_id=company.id).all()
    return jsonify([{
        "id": j.id,
        "job_title": j.job_title,
        "status": j.status,
        "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None,
        "total_applications": len(j.applications)
    } for j in jobs])


@company_bp.route('/jobs', methods=['POST'])
@role_required('company')
def create_job():
    company = get_current_company()
    data = request.get_json()
    deadline = datetime.fromisoformat(data['application_deadline'])
    job = Job(
        company_id=company.id,
        job_title=data['job_title'],
        job_description=data.get('job_description'),
        skills_required=data.get('skills_required'),
        salary=data.get('salary'),
        eligible_branches=data.get('eligible_branches'),
        min_cgpa=data.get('min_cgpa', 0.0),
        eligible_year=data.get('eligible_year'),
        application_deadline=deadline,
        status='pending'
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({"message": "Job posted successfully, awaiting admin approval", "job_id": job.id}), 201


@company_bp.route('/jobs/<int:job_id>/close', methods=['PATCH'])
@role_required('company')
def close_job(job_id):
    company = get_current_company()
    job = Job.query.filter_by(id=job_id, company_id=company.id).first_or_404()
    job.status = 'closed'
    db.session.commit()
    return jsonify({"message": f"Job '{job.job_title}' closed"})


@company_bp.route('/jobs/<int:job_id>/applications', methods=['GET'])
@role_required('company')
def view_applications(job_id):
    company = get_current_company()
    job = Job.query.filter_by(id=job_id, company_id=company.id).first_or_404()
    return jsonify([{
        "application_id": a.id,
        "student_name": a.student.full_name,
        "student_id": a.student_id,
        "branch": a.student.branch,
        "cgpa": a.student.cgpa,
        "status": a.status,
        "feedback": a.feedback,
        "interview_datetime": a.interview_datetime.isoformat() if a.interview_datetime else None,
        "application_date": a.application_date.isoformat() if a.application_date else None
    } for a in job.applications])


@company_bp.route('/applications/<int:app_id>/update', methods=['PATCH'])
@role_required('company')
def update_application(app_id):
    data = request.get_json()
    application = Application.query.get_or_404(app_id)
    if 'status' in data:
        application.status = data['status']  # shortlisted / selected / rejected
    if 'feedback' in data:
        application.feedback = data['feedback']
    if 'interview_datetime' in data:
        application.interview_datetime = datetime.fromisoformat(data['interview_datetime'])
    db.session.commit()
    return jsonify({"message": "Application updated"})
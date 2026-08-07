from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import get_jwt_identity
from backend import db
from backend.models import Student, Job, Application, Placement, User
from backend.utils import role_required
from werkzeug.utils import secure_filename
import os

student_bp = Blueprint('student', __name__, url_prefix='/api/student')


def get_current_student():
    user_id = get_jwt_identity()
    return Student.query.filter_by(user_id=int(user_id)).first()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@student_bp.route('/profile', methods=['GET'])
@role_required('student')
def get_profile():
    student = get_current_student()
    return jsonify({
        "id": student.id,
        "full_name": student.full_name,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "graduation_year": student.graduation_year,
        "skills": student.skills,
        "phone": student.phone,
        "resume_path": student.resume_path
    })


@student_bp.route('/profile', methods=['PUT'])
@role_required('student')
def update_profile():
    student = get_current_student()
    data = request.get_json()
    student.full_name = data.get('full_name', student.full_name)
    student.branch = data.get('branch', student.branch)
    student.cgpa = data.get('cgpa', student.cgpa)
    student.graduation_year = data.get('graduation_year', student.graduation_year)
    student.skills = data.get('skills', student.skills)
    student.phone = data.get('phone', student.phone)
    db.session.commit()
    return jsonify({"message": "Profile updated successfully"})


@student_bp.route('/profile/resume', methods=['POST'])
@role_required('student')
def upload_resume():
    student = get_current_student()
    if 'resume' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files['resume']
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF, DOC, DOCX allowed"}), 400
    filename = secure_filename(f"student_{student.id}_{file.filename}")
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, filename))
    student.resume_path = filename
    db.session.commit()
    return jsonify({"message": "Resume uploaded", "filename": filename})


@student_bp.route('/profile/resume', methods=['GET'])
@role_required('student')
def download_resume():
    student = get_current_student()
    if not student.resume_path:
        return jsonify({"error": "No resume uploaded"}), 404
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], student.resume_path)


@student_bp.route('/jobs', methods=['GET'])
@role_required('student')
def list_jobs():
    search = request.args.get('search', '')
    query = Job.query.filter_by(status='approved')
    if search:
        query = query.filter(
            (Job.job_title.ilike(f'%{search}%')) |
            (Job.skills_required.ilike(f'%{search}%'))
        )
    jobs = query.all()
    return jsonify([{
        "id": j.id,
        "company_name": j.company.company_name,
        "job_title": j.job_title,
        "job_description": j.job_description,
        "skills_required": j.skills_required,
        "salary": j.salary,
        "eligible_branches": j.eligible_branches,
        "min_cgpa": j.min_cgpa,
        "eligible_year": j.eligible_year,
        "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None
    } for j in jobs])


@student_bp.route('/apply/<int:job_id>', methods=['POST'])
@role_required('student')
def apply_job(job_id):
    student = get_current_student()

    if student.is_blacklisted:
        return jsonify({"error": "You are blacklisted from applying"}), 403

    job = Job.query.filter_by(id=job_id, status='approved').first_or_404()

    # eligibility checks
    if student.cgpa and job.min_cgpa and student.cgpa < job.min_cgpa:
        return jsonify({"error": f"Minimum CGPA required: {job.min_cgpa}"}), 403

    if job.eligible_branches and student.branch:
        allowed = [b.strip() for b in job.eligible_branches.split(',')]
        if student.branch not in allowed:
            return jsonify({"error": f"Your branch is not eligible for this job"}), 403

    # duplicate application check (belt-and-suspenders, DB constraint also prevents this)
    existing = Application.query.filter_by(
        student_id=student.id,
        job_position_id=job_id
    ).first()
    if existing:
        return jsonify({"error": "You have already applied for this job"}), 400

    application = Application(student_id=student.id, job_position_id=job_id)
    db.session.add(application)
    db.session.commit()
    return jsonify({"message": "Application submitted successfully", "application_id": application.id}), 201


@student_bp.route('/applications', methods=['GET'])
@role_required('student')
def my_applications():
    student = get_current_student()
    apps = Application.query.filter_by(student_id=student.id).all()
    return jsonify([{
        "application_id": a.id,
        "company_name": a.job_position.company.company_name,
        "job_title": a.job_position.job_title,
        "status": a.status,
        "feedback": a.feedback,
        "interview_datetime": a.interview_datetime.isoformat() if a.interview_datetime else None,
        "application_date": a.application_date.isoformat() if a.application_date else None
    } for a in apps])


@student_bp.route('/offer-letter/<int:app_id>', methods=['GET'])
@role_required('student')
def offer_letter(app_id):
    student = get_current_student()
    application = Application.query.filter_by(
        id=app_id,
        student_id=student.id,
        status='selected'
    ).first_or_404()
    return jsonify({
        "offer_letter": {
            "student_name": student.full_name,
            "company_name": application.job_position.company.company_name,
            "job_title": application.job_position.job_title,
            "salary": application.job_position.salary,
            "message": f"Congratulations {student.full_name}! You have been selected for the position of {application.job_position.job_title} at {application.job_position.company.company_name}."
        }
    })

@student_bp.route('/history', methods=['GET'])
@role_required('student')
def placement_history():
    student = get_current_student()
    apps = Application.query.filter_by(student_id=student.id).all()
    return jsonify([{
        "application_id": a.id,
        "company_name": a.job_position.company.company_name,
        "job_title": a.job_position.job_title,
        "salary": a.job_position.salary,
        "application_date": a.application_date.isoformat() if a.application_date else None,
        "status": a.status,
        "feedback": a.feedback,
        "interview_datetime": a.interview_datetime.isoformat() if a.interview_datetime else None
    } for a in apps])

from backend.tasks.export import export_applications_csv

@student_bp.route('/export', methods=['POST'])
@role_required('student')
def trigger_export():
    student = get_current_student()
    task = export_applications_csv.delay(student.id)
    return jsonify({
        "message": "Export started. You will receive an email when done.",
        "task_id": task.id
    }), 202

from backend import celery as celery_app

@student_bp.route('/task-status/<task_id>', methods=['GET'])
@role_required('student')
def student_task_status(task_id):
    task = celery_app.AsyncResult(task_id)
    return jsonify({
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    })
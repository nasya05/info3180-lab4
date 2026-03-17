import os
from flask import render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from app import app, db, login_manager
from app.models import UserProfile
from app.forms import LoginForm, UploadForm

# ---------------- Helper Functions ----------------

def get_uploaded_images():
    """Returns a list of filenames in the uploads folder."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_list = []
    for subdir, dirs, files in os.walk(upload_folder):
        for file in files:
            file_list.append(file)
    return file_list

# ---------------- Routes ----------------

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about/')
def about():
    return render_template('about.html', name="Mary Jane")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = UserProfile.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("You have successfully logged in!", "success")
            return redirect(url_for('upload'))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html", form=form)

@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.photo.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # Ensure upload folder exists
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])

        file.save(filepath)
        flash("File uploaded successfully!", "success")
        return redirect(url_for('files'))

    return render_template("upload.html", form=form)

@app.route('/uploads/<filename>')
@login_required
def get_image(filename):
    """Serve a specific uploaded image."""
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        filename
    )

@app.route('/logout')
@login_required
def logout():
    """Logs out the current user and redirects to home."""
    logout_user()  # Flask-Login method to log out the user
    flash("You have been logged out.", "success")  # Flash a message
    return redirect(url_for('home'))  # Redirect to homepage

@app.route('/files')
@login_required
def files():
    """Lists all uploaded images."""
    images = get_uploaded_images()
    return render_template("files.html", images=images)

# Optional: Flash form errors
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in the {getattr(form, field).label.text} field - {error}", "danger")
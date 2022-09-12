from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm, DeleteForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "scoobydoo"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return redirect('/register')


@app.route('/users/<username>')
def user_page(username):
    if 'username' not in session:      
        flash("Please login first!", 'danger')
        return redirect('/login')
    else:
        user = User.query.get(username)
        form = FeedbackForm()
        return render_template('user_info.html', user=user, form=form)

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if 'username' in session:
        return redirect(f"/users/{session['username']}")
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        new_user = User.register(username, password, first_name, last_name, email)

        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username
        flash('Welcome! Successfully Created Your Account!', 'success')
        return redirect(f"/users/{new_user.username}")

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", 'primary')
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    flash('Goodbye!', 'info')
    return redirect('/login')

@app.route('/users/<username>/delete', methods=['POST'])
def remove_user(username):

    if 'username' not in session:      
        flash("Please login first!", 'danger')
        return redirect('/login')
    else:
        user = User.query.get(username)
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        return redirect('/login')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def new_feedback(username):
    if 'username' not in session:      
        flash("Please login first!", 'danger')
        return redirect('/login')

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(
            title=title,
            content=content,
            username=username)

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    else:
        return render_template('new_feedback.html', form=form)

@app.route("/feedback/<int:feedback_id>/update", methods=['GET', 'POST'])
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)

    if 'username' not in session:      
        flash("Please login first!", 'danger')
        return redirect('/login')

    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()

        return redirect(f'/users/{feedback.username}')

    return render_template('edit_feedback.html', form=form, feedback=feedback)

# @app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
# def delete_feedback(feedback_id):
#     feedback = Feedback.query.get(feedback_id)
#     if 'username' not in session:      
#         flash("Please login first!", 'danger')
#         return redirect('/login')

#     form = DeleteForm()
#     if form.validate_on_submit():
#         db.session.delete(feedback)
#         db.session.commit()

#     return redirect(f'/users/{feedback.username}')


@app.route('/feedback/<int:feedback_id>/delete')
def delete_feedback(feedback_id):
    if 'username' not in session:      
        flash("Please login first!", 'danger')
        return redirect('/login')
    
    else:
        feedback = Feedback.query.get(feedback_id)
        db.session.delete(feedback)
        db.session.commit()
        session.pop('feedback')
        return redirect(f'/users/{feedback.username}')



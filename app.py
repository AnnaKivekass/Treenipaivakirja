from flask import Flask, render_template, redirect, url_for, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, WorkoutForm, MessageForm
from models import db, User, Workout, Message

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workout_diary.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', workouts=workouts)

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/workout/add', methods=['GET','POST'])
@login_required
def add_workout():
    form = WorkoutForm()
    if form.validate_on_submit():
        workout = Workout(
            date=form.date.data,
            type=form.type.data,
            duration=form.duration.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(workout)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('workout_form.html', form=form)

@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    form = MessageForm()
    if form.validate_on_submit():
        new_message = Message(content=form.content.data, user_id=current_user.id)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('messages'))

    all_messages = Message.query.all()
    return render_template('messages.html', form=form, messages=all_messages)

@app.route('/edit_message/<int:message_id>', methods=['GET', 'POST'])
@login_required
def edit_message(message_id):
    message = Message.query.get_or_404(message_id)
    if message.user_id != current_user.id:
        abort(403)
    form = MessageForm()
    if form.validate_on_submit():
        message.content = form.content.data
        db.session.commit()
        return redirect(url_for('messages'))

    form.content.data = message.content
    return render_template('edit_message.html', form=form, message=message)


@app.route('/delete_message/<int:message_id>')
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    if message.user_id != current_user.id:
        abort(403)

    db.session.delete(message)
    db.session.commit()
    return redirect(url_for('messages'))

@app.route('/search')
@login_required
def search():
    query = request.args.get('query')
    if query:
        results = Workout.query.filter(
            (Workout.type.ilike(f"%{query}%")) |
            (Workout.description.ilike(f"%{query}%")) |
            (Workout.date.ilike(f"%{query}%"))
        ).filter_by(user_id=current_user.id).all()
    else:
        results = []
    return render_template('search.html', query=query, results=results)

@app.route('/user/<int:user_id>')
@login_required
def show_user(user_id):
    user = User.query.get_or_404(user_id)
    workouts = Workout.query.filter_by(user_id=user_id).order_by(Workout.date.desc()).all()
    return render_template('user.html', user=user, workouts=workouts)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


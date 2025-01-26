from flask import Flask, render_template, request, redirect, flash, session
from earn import User, get_tasks
from feedback import FeedbackManager
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "hi"
feedback_manager = FeedbackManager()

def get_user():
    if 'username' not in session:
        session['username'] = 'NewUser'
    username = session['username']
    return User(username)

@app.route('/')
def home():
    return redirect('/rewards/earn')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback_page():
    if request.method == 'POST':
        rating1 = request.form.get('rating1')
        rating2 = request.form.get('rating2')
        feedback_text = request.form.get('feedback_text')

        if feedback_manager.validate(rating1, rating2, feedback_text):
            feedback_manager.save_feedback(rating1, rating2, feedback_text)
            flash("Thank you for your feedback!", "success")
            return redirect('/feedback')
        else:
            for error in feedback_manager.errors:
                flash(error, "danger")
    return render_template('cusfb.html')

@app.route('/admin')
def admin_page():
    feedback_list = feedback_manager.get_all_feedback()
    return render_template('adminfb.html', feedback=feedback_list)

@app.route('/rewards/earn')
def rewards():
    user = get_user()
    tasks = get_tasks()
    streak = session.get('streak', user.streak)
    return render_template('rewards.html', section='earn', data={'tasks': tasks}, user_data={
        'username': user.username,
        'total_points': session.get('total_points', user.total_points),  # Use session for points
        'daily_points': user.daily_points,
        'streak': streak
    })

@app.route('/rewards/redeem', methods=['GET', 'POST'])
def redeem():
    user = get_user()
    streak = session.get('streak', user.streak)
    if request.method == 'POST':
        reward_name = request.form['reward_name']
        reward_points = int(request.form['reward_points'])

        if user.total_points >= reward_points:
            user.total_points -= reward_points
            session['total_points'] = user.total_points
            user.save()
            flash(f"Successfully redeemed {reward_name} for {reward_points} points!", "success")
        else:
            flash("Not enough points to redeem this reward.", "danger")

    rewards = [
        {'name': 'Voucher A', 'points': 50},
        {'name': 'Voucher B', 'points': 100},
        {'name': 'Voucher C', 'points': 150}
    ]
    return render_template('redeem.html', rewards=rewards, user_data={
        'username': user.username,
        'total_points': user.total_points,
        'streak': streak  # Use streak from session
    })

@app.route('/rewards/earn/quiz', methods=['GET', 'POST'])
def quiz():
    user = get_user()
    total_points = 0
    score = 0

    last_quiz_time = session.get(f'{user.username}_last_quiz_time', None)
    if last_quiz_time is not None:
        last_quiz_time = last_quiz_time.replace(tzinfo=None)
        if datetime.now() - last_quiz_time < timedelta(days=1) and user.streak > 0:
            flash("You can only take the quiz once every 24 hours.", "danger")
            return redirect('/rewards/earn')

    if request.method == 'POST':
        answer_1 = request.form.get('answer_1')
        answer_2 = request.form.get('answer_2')

        if answer_1 == 'train':
            score += 1
            total_points += 25
        if answer_2 == 'sweden':
            score += 1
            total_points += 25

        if score == 2:
            user.total_points += total_points
            user.streak += 1
            session['total_points'] = user.total_points
            session['streak'] = user.streak

            user.save()

            flash(f"You got {score} out of 2 questions right! {total_points} points added.", "success")
            session[f'{user.username}_last_quiz_time'] = datetime.now()
        else:
            flash(f"You got {score} out of 2 questions right. Try again!", "danger")

        return redirect('/rewards/earn')

    return render_template('quiz.html')


@app.route('/reset_cd', methods=['GET'])
def reset_cd():
    user = get_user()
    session[f'{user.username}_last_quiz_time'] = None
    flash("Cooldown reset. You can now retake the quiz.", "success")
    return redirect('/rewards/earn')

@app.route('/reset_streak', methods=['GET'])
def reset_streak():
    user = get_user()
    user.total_points = 0
    user.daily_points = 0
    user.streak = 0

    session['streak'] = user.streak
    session['total_points'] = user.total_points

    user.save()

    flash("Streak and points have been reset.", "success")
    return redirect('/rewards/earn')


if __name__ == '__main__':
    app.run(debug=True)

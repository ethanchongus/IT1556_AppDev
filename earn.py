from datetime import datetime
from flask import session

now = datetime.now()

class Task:
    def __init__(self, name, description, points):
        self.name = name
        self.description = description
        self.points = points

class User:
    def __init__(self, username):
        self.username = username
        self.total_points = session.get(f'{username}_total_points', 0)
        self.daily_points = session.get(f'{username}_daily_points', 0)
        self.streak = session.get(f'{username}_streak', 0)
        self.last_completed = session.get(f'{username}_last_completed', None)
        self.last_streak_update = session.get(f'{username}_last_streak_update', None)  # NEW

    def save(self):
        session[f'{self.username}_total_points'] = self.total_points
        session[f'{self.username}_daily_points'] = self.daily_points
        session[f'{self.username}_streak'] = self.streak
        session[f'{self.username}_last_completed'] = self.last_completed
        session[f'{self.username}_last_streak_update'] = self.last_streak_update  # NEW

    def complete_task(self, task):
        today = datetime.today().date()

        # Award points normally
        self.total_points += task.points
        self.daily_points += task.points

        # Increase streak ONLY if it's the first task of the day
        if self.last_streak_update != str(today):
            self.streak += 1
            self.last_streak_update = str(today)

        self.save()


tasks = [
    Task("Complete Profile", "Fill out your profile information", 10),
    Task("Share on Social Media", "Share your referral link", 20),
    Task("Invite a Friend", "Invite a friend to the site", 30)
]

def get_tasks():
    return [
        {
            'name': 'Eco Tour Quiz',
            'description': 'Complete the Eco Tour themed quiz to earn points.',
            'points': 50
        }
    ]

def complete_task(user, task_name):
    task = next((t for t in tasks if t.name == task_name), None)
    if task:
        user.complete_task(task)
        user.save()
        return True
    return False

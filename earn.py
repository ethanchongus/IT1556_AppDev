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

    def save(self):
        session[f'{self.username}_total_points'] = self.total_points
        session[f'{self.username}_daily_points'] = self.daily_points
        session[f'{self.username}_streak'] = self.streak
        session[f'{self.username}_last_completed'] = self.last_completed

    def complete_task(self, task):
        self.total_points += task.points
        self.daily_points += task.points

        today = datetime.today().date()
        if self.last_completed != today:
            self.streak += 1
            self.last_completed = today
        else:
            self.daily_points = task.points


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

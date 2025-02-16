#testot
import shelve
from datetime import datetime
class FeedbackManager:
    def __init__(self):
        self.db_name = 'feedback_store'
        self.errors = []

    def validate(self, experience, recommendation, suggestion):
        self.errors = []

        if experience not in ['1', '2', '3', '4', '5']:
            self.errors.append("Please select a rating between 1 and 5 for Question 1.")

        if recommendation not in ['1', '2', '3', '4', '5']:
            self.errors.append("Please select a rating between 1 and 5 for Question 2.")

        if not suggestion or len(suggestion.strip()) == 0:
            self.errors.append("Please provide feedback in the text box for Question 3.")

        return len(self.errors) == 0
    def get_all_feedback(self):
        with shelve.open(self.db_name) as db:
            feedback = list(db.values())
            print(feedback)
            return feedback

    def save_feedback(self, experience, recommendation, suggestion):
        with shelve.open(self.db_name) as db:
            feedback_id = str(len(db)+1)
            db[feedback_id] = {
                'experience': experience,
                'recommendation': recommendation,
                'suggestion': suggestion,
                'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }



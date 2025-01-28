import shelve
from datetime import datetime


class FeedbackManager:
    def __init__(self):
        self.db_name = 'feedback_store'
        self.errors = []

    def validate(self, experience, recommendation, suggestion):

        self.errors = []

        if experience not in ['1', '2', '3', '4', '5']:
            if experience == "":
                self.errors.append("Please select a rating for your website experience (Question 1).")
            else:
                self.errors.append("Invalid input for website experience. Please select a value between 1 and 5.")

        if recommendation not in ['1', '2', '3', '4', '5']:
            if recommendation == "":
                self.errors.append("Please select a rating for likelihood to recommend us (Question 2).")
            else:
                self.errors.append("Invalid input for recommendation. Please select a value between 1 and 5.")

        if not suggestion or len(suggestion.strip()) == 0:
            self.errors.append("Please provide feedback or suggestions in the text box (Question 3).")

        if experience and recommendation == "" and not suggestion:
            self.errors.append("You answered Question 1 but left Question 2 and Question 3 blank.")
        elif recommendation and experience == "" and not suggestion:
            self.errors.append("You answered Question 2 but left Question 1 and Question 3 blank.")
        elif suggestion and experience == "" and recommendation == "":
            self.errors.append("You answered Question 3 but left Question 1 and Question 2 blank.")

        return len(self.errors) == 0

    def get_all_feedback(self):

        with shelve.open(self.db_name) as db:
            feedback = {key: db[key] for key in db}  # Retrieve all feedback with IDs
        return feedback

    def save_feedback(self, experience, recommendation, suggestion):

        with shelve.open(self.db_name) as db:
            feedback_id = str(len(db) + 1)
            db[feedback_id] = {
                'rating1': experience,
                'rating2': recommendation,
                'feedback': suggestion.strip(),
                'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }

    def reply_to_feedback(self, feedback_id, reply):

        with shelve.open(self.db_name, writeback=True) as db:
            if feedback_id in db:
                db[feedback_id]['reply'] = reply
            else:
                raise KeyError(f"Feedback ID {feedback_id} not found.")

    def delete_feedback(self, feedback_id):

        with shelve.open(self.db_name, writeback=True) as db:
            if feedback_id in db:
                del db[feedback_id]
            else:
                raise KeyError(f"Feedback ID {feedback_id} not found.")


if __name__ == "__main__":
    manager = FeedbackManager()

    experience = "4"
    recommendation = ""
    suggestion = ""

    if manager.validate(experience, recommendation, suggestion):
        manager.save_feedback(experience, recommendation, suggestion)
        print("Feedback submitted successfully!")
    else:
        print("Errors:")
        for error in manager.errors:
            print(f"- {error}")




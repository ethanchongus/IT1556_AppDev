import shelve

class FeedbackManager:
    def __init__(self, db_path='database/feedback.db'):
        """ Initializes the FeedbackManager with a database path """
        self.db_path = db_path

    def get_all_feedback(self):
        """ Retrieves all feedback stored in the database """
        with shelve.open(self.db_path) as db:
            return db.get('Feedback', {})  # Return an empty dict if no feedback exists

    def save_feedback(self, rating1, rating2, feedback_text):
        """ Saves feedback to the database """
        with shelve.open(self.db_path, writeback=True) as db:
            feedback_dict = db.get('Feedback', {})

            # Generate a unique feedback ID
            feedback_id = str(len(feedback_dict) + 1)

            # Store feedback details
            feedback_dict[feedback_id] = {
                'id': feedback_id,
                'rating1': rating1,
                'rating2': rating2,
                'feedback_text': feedback_text
            }

            # Save back to database
            db['Feedback'] = feedback_dict

    def delete_feedback(self, feedback_id):
        """ Deletes feedback by ID """
        with shelve.open(self.db_path, writeback=True) as db:
            feedback_dict = db.get('Feedback', {})

            print(f"DEBUG: Existing Feedback IDs before deletion: {feedback_dict.keys()}")  # ✅ Debugging step

            if str(feedback_id) in feedback_dict:  # Convert to string for consistency
                del feedback_dict[str(feedback_id)]  # Ensure ID is removed as a string key
                db['Feedback'] = feedback_dict  # Save changes

                print(f"DEBUG: Feedback deleted successfully: {feedback_id}")  # ✅ Debugging step
                return True  # ✅ Successfully deleted

            print(f"DEBUG: Feedback ID {feedback_id} not found.")  # ✅ Debugging step
            return False  # ❌ Feedback ID not found

    def validate(self, rating1, rating2, feedback_text):
        """ Validates the feedback form fields """
        self.errors = []  # Reset errors

        # Validate rating1 (must be between 1 and 5)
        if not rating1 or not rating1.isdigit() or int(rating1) not in range(1, 6):
            self.errors.append("Service rating must be between 1 and 5.")

        # Validate rating2 (must be between 1 and 5)
        if not rating2 or not rating2.isdigit() or int(rating2) not in range(1, 6):
            self.errors.append("Product rating must be between 1 and 5.")

        # Validate feedback text (must not be empty)
        if not feedback_text.strip():
            self.errors.append("Feedback text cannot be empty.")

        return len(self.errors) == 0  # Returns True if no errors

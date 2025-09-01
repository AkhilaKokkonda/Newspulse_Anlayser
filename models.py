
# from app import db
# from flask_login import UserMixin
# from datetime import datetime

# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(150), unique=True, nullable=False)
#     email = db.Column(db.String(150), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)
#     interested_area = db.Column(db.String(150))

#     # Relationship: One user can have many reports
#     reports = db.relationship('Report', backref='author', lazy=True)

#     def __repr__(self):
#         return f"<User {self.username}>"


# class Report(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     text = db.Column(db.Text, nullable=False)
#     sentiment = db.Column(db.String(100))
#     entities = db.Column(db.Text)  # storing as plain text; could also use JSON
#     date_created = db.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return f"<Report {self.id} by User {self.user_id}>"


# from app import db
# from flask_login import UserMixin
# from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash
# import json

# class User(db.Model, UserMixin):
#     __tablename__ = 'user'

#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(150), unique=True, nullable=False, index=True)
#     email = db.Column(db.String(150), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(200), nullable=False)
#     interested_area = db.Column(db.String(150))

#     # Relationship: One user can have many reports
#     reports = db.relationship('Report', backref='author', lazy=True)

#     def set_password(self, password):
#         """Hashes and sets the user password."""
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         """Verifies the password against the stored hash."""
#         return check_password_hash(self.password_hash, password)

#     def __repr__(self):
#         return f"<User {self.username}>"


# class Report(db.Model):
#     __tablename__ = 'report'

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     text = db.Column(db.Text, nullable=False)

#     # Sentiment details
#     sentiment = db.Column(db.String(100))  # POSITIVE / NEUTRAL / NEGATIVE
#     sentiment_score = db.Column(db.Float)  # Confidence score

#     # Entities stored as JSON string for flexibility
#     entities = db.Column(db.Text)  # JSON serialized text

#     date_created = db.Column(db.DateTime, default=datetime.utcnow)
#     last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     def set_entities(self, entity_list):
#         """Stores entities as JSON."""
#         self.entities = json.dumps(entity_list)

#     def get_entities(self):
#         """Returns entities as Python list."""
#         return json.loads(self.entities or "[]")

#     def __repr__(self):
#         return f"<Report {self.id} by User {self.user_id}>"



# from app import db
# from flask_login import UserMixin
# from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash
# import json


# class User(db.Model, UserMixin):
#     __tablename__ = 'user'

#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(150), unique=True, nullable=False, index=True)
#     email = db.Column(db.String(150), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(200), nullable=False)
#     interested_area = db.Column(db.String(150))  # e.g., "Technology", "Finance"

#     # Relationship: One user can have many reports
#     reports = db.relationship('Report', backref='author', lazy=True, cascade="all, delete-orphan")

#     def set_password(self, password: str):
#         """Hashes and sets the user password."""
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password: str) -> bool:
#         """Verifies the password against the stored hash."""
#         return check_password_hash(self.password_hash, password)

#     def __repr__(self):
#         return f"<User {self.username} | {self.email}>"


# class Report(db.Model):
#     __tablename__ = 'report'

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

#     # Core report content
#     text = db.Column(db.Text, nullable=False)  # news article / trend text

#     # Sentiment details
#     sentiment = db.Column(db.String(100))  # POSITIVE / NEUTRAL / NEGATIVE
#     sentiment_score = db.Column(db.Float)  # Confidence score (0.0–1.0)

#     # Entities stored as JSON string for flexibility
#     entities = db.Column(db.Text)  # JSON serialized text (list of entities)

#     # Optional field for downloadable report file
#     file_path = db.Column(db.String(200), nullable=True)

#     # Timestamps
#     date_created = db.Column(db.DateTime, default=datetime.utcnow)
#     last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     def set_entities(self, entity_list: list):
#         """Stores entities as JSON string."""
#         self.entities = json.dumps(entity_list)

#     def get_entities(self) -> list:
#         """Returns entities as a Python list."""
#         return json.loads(self.entities or "[]")

#     def __repr__(self):
#         return (
#             f"<Report {self.id} | User {self.user_id} | "
#             f"Sentiment={self.sentiment} | Created={self.date_created.strftime('%Y-%m-%d')}>"
#         )


from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    interested_area = db.Column(db.String(150))  # e.g., "Technology", "Finance"

    def set_password(self, password: str):
        """Hashes and sets the user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifies the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} | {self.email}>"

import os
from sqlalchemy import Column, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

database_name = "trivia"
database_path = "postgres://postgres@{}/{}".format('localhost:5432', database_name)
db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    """
    binds a flask application and a SQLAlchemy service
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    return db


'''
Question

'''


class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(db.String, nullable=False)
    answer = Column(db.String, nullable=False)
    category = Column(Integer, nullable=False)
    difficulty = Column(Integer, nullable=False)

    def __init__(self, question, answer, category, difficulty):
        if not isinstance(question, str) or not isinstance(answer, str):
            raise ValueError("question and answer should be string")
        if not isinstance(category, int) or not isinstance(difficulty, int):
            raise ValueError("category and difficulty should be int")
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }


'''
Category

'''


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(db.String, nullable=False)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }

from flask import request, jsonify, abort
from models import Question, Category, db
from flaskr import QUESTIONS_PER_PAGE
from flask_cors import cross_origin
from . import main as app


@app.route('/')
def index():
    return 'Hello Trivia!'


@app.route('/questions', methods=['GET'])
def question_list():
    """
        The request should include params in url. questions are filtered by category, and the specific page
        will be returned. QUESTIONS_PER_PAGE specifies how many questions a page bears.
        `page`: integer. if invalid, return the first page.
        `current_category`: 'null' for all categories, integer for a particular category ID.
        `search_term`: a string to search in question descriptions if not empty.
    :return: {
        questions: { question, answer, category, difficulty }
        total_questions: the number of all questions selected.
        page: the actual returned page.
        }
    """
    f = request.values
    query = Question.query

    try:
        page = int(f['page'])
        if f['current_category'] != 'null':
            current_category = int(f['current_category'])
            assert current_category > 0
        else:
            current_category = None
        if f['search_term']:
            search = "%{}%".format(f['search_term'])
        else:
            search = ''
    except Exception:
        abort(422)
        return

    try:
        if search:
            query = query.filter(Question.question.ilike(search))
        if current_category:
            query = query.filter_by(category=current_category)

        questions = query.all()
        total_questions = len(questions)
        max_page = total_questions // QUESTIONS_PER_PAGE + (1 if total_questions % QUESTIONS_PER_PAGE > 0 else 0)
        if page > max_page or page < 1:
            page = 1
        questions = questions[(page-1) * QUESTIONS_PER_PAGE: page * QUESTIONS_PER_PAGE]

        return jsonify({
            'questions': [q.format() for q in questions],
            'total_questions': total_questions,
            'page': page,
            'message': 'OK'
        }), 200
    except Exception:
        abort(500)


@app.route('/categories', methods=['GET'])
def category_list():
    """
    :return: `categories`: dictionary with
    """
    categories = Category.query.order_by('id').all()
    return jsonify({
        'message': 'OK',
        'categories': [c.format() for c in categories]
    }), 200


@app.route('/questions/<int:id>', methods=['DELETE'])
def question_delete(id):
    to_delete = Question.query.get(id)
    if to_delete is None:
        abort(404)
    try:
        to_delete.delete()      # delete and commit
        return jsonify({
            'message': 'OK'
        }), 200
    except Exception:
        db.session.rollback()
        abort(500)



@app.route('/questions', methods=['POST'])
def question_create():
    f = request.get_json()
    try:
        q = Question(**f)
    except TypeError:
        abort(422)
        return
    except ValueError:
        abort(422)
        return
    try:
        q.insert()
        return jsonify({
            'message': 'Created'
        }), 201
    except Exception:
        db.session.roll_back()
        abort(500)


@app.route('/quizzes', methods=['POST'])
def quiz_get_next():
    import random
    f = request.get_json()
    previous_questions = f['previous_questions']
    quiz_category = int(f['category'])
    query = Question.query
    if quiz_category != -1:
        query = query.filter_by(category=quiz_category)
    quiz_list = query.all()
    quiz_list = [q for q in quiz_list if q.id not in previous_questions]

    return jsonify({
        'message': 'OK',
        'question': None if not quiz_list else random.choice(quiz_list).format(),
    }), 200


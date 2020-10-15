# Full Stack Trivia API Backend

## Getting Started
The backend of the Trivia project runs locally. 
Therefore, the backend APIs' `Base URL` is `localhost:5000`, 
which is the default URL that flask runs in developmental environment.
There's no API Keys or authentication settings to specify.

### Installing Dependencies


#### Python 3.7
Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment
We recommend working within a virtual environment whenever using Python for projects. 
This keeps your dependencies for each project separate and organaized. 
Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)


#### PIP Dependencies
Once you have your virtual environment setup and running, install dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.
Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Errors
This project uses standard HTTP status codes to describe errors. If an error is triggered, a json object with key `error`
and `message` will be returned to the client. 

|response code | message | error|
|---|---|---|
|400|"Bad Request"|400|
|422|"Unprocessable Entity"|422|
|404|"Not Found"|404|
|500|"Internal Server Error"|500|


## Endpoints
The following section introduced all endpoints, how to send a request to them and their response.
All responses are in json. **Here we use `result` to refer that json object.**

### GET '/categories'
- Fetches a list of categories which contain field `id` and `type`.
- `id`: The unique identifier for a category in the database. Integer.
- `type`: The corresponding string representing the category. String.
#### Request Arguments
None.
#### Response
- `result.categories`
    - A list of objects. Each object has two keys: `id` and `type`. 
    - Example:
        ```
      [
        {'id':1, 'type':"Science"},
        {'id':2, 'type': "Art"},
        {'id':3, 'type': "Geography"},
        {'id':4, 'type': "History"},
        {'id':5, 'type': "Entertainment"},
        {'id':6, 'type': "Sports"},
      ]
        ```
- `result.message`: 'OK'
- response code: 200



### GET '/questions'
- Fetches a list of questions of a specific page. Each page contains 10 questions.
- The request could include some parameters in URL to filter return questions by `current_category` and `search_term`. 
#### Request Arguments
- `current_category`: Integer. Specified the ID of the category of interest. If set to `null`, allow all categories.
- `search_term`: String. Search by any phrase. The questions list will update to include only question that include that string within their question. If empty, there is no restriction on question title.
- `page`: Integer. If invalid, set to 1 by default.
#### Response
- `result.result.questions`: The specific page of questions filtered by `current_category` and `search_term`.
- `result.total_questions`: the number of all questions selected.
- `result.page`: The actual returned page. If the requested `page` is invalid, 1 will be returned.
- `result.message`: 'OK'
- response code: 200


### DELETE '/questions/<id>'
- Delete a question by its ID.
#### Request Arguments
- Just specify `id` in URL. Example: `/questions/15`
#### Response
- `result.message`: 'OK'
- response code: 200

### POST '/questions'
- Create a new questions. Require the question and answer text, category, and difficulty score.
#### Request Arguments
- `question`: String. The title of the question.
- `answer`: String. The answer to the question.
- `category`: Integer. The ID of the question's category.
- `difficulty`: Integer from 1 to 5. How difficult is that question. 1 for the easiest and 5 for the hardest.
#### Response
- `result.message`: 'Created'
- response code: 201


### POST '/quizzes'
- Get the next question to play the quiz. 
- This endpoint take category and previous question as parameters and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
#### Request Arguments
- `previous_questions`: List of integers. IDs of previously answered questions.
- `category`: Integer. The ID of the quiz's category. -1 for all categories.
#### Response
- `result.question`: A question object with keys `question`, `answer`, `category` and `difficulty`. 
`result.question` can also be Null, which means there is no valid questions unanswered, the game is forced to end.
- response code: 200



## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
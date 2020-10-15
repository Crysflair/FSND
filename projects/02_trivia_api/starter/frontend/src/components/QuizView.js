import React, { Component } from 'react';
import $ from 'jquery';

import '../stylesheets/QuizView.css';



class QuizView extends Component {
  constructor(props){
    super();
    this.state = {
        category: -1,             // selected category, -1 for all
        previousQuestions: [],      // ids of previous questions.
        showAnswer: false,
        categories: [],             // all categories
        numCorrect: 0,
        currentQuestion: null,
        guess: '',
        forceEnd: false,
        questionPerPlay: 5,      // positive for total question per play, -1 for endless game. default 5
    }
  }

  componentDidMount(){
    $.ajax({
      url: `/categories`,
      type: "GET",
      success: (result) => {
        this.setState({ categories: result.categories });
      },
      error: (error) => {
        alert('Unable to load categories. Please try your request again');
      }
    })
  }

  handleChange = (event) => {
    this.setState({[event.target.name]: event.target.value})
  }

  getNextQuestion = () => {
    const previousQuestions = [...this.state.previousQuestions];
    if(this.state.currentQuestion) { previousQuestions.push(this.state.currentQuestion.id) }
    this.setState({previousQuestions: previousQuestions},
        // refresh the previousQuestions before request new quizzes
        () => {
            $.ajax({
      url: '/quizzes',
      type: "POST",
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify({
        previous_questions: this.state.previousQuestions,
        category: this.state.category
      }),
      xhrFields: {
        withCredentials: true
      },
      crossDomain: true,
      success: (result) => {
        this.setState({
          showAnswer: false,
          currentQuestion: result.question,
          guess: '',
          forceEnd: !result.question
        });
      },
      error: (error) => {
        alert('Unable to load question. Please try your request again');
      }
    })
        }
    );
  };

  submitGuess = (event) => {
    event.preventDefault();
    let evaluate =  this.evaluateAnswer();
    this.setState({
      numCorrect: !evaluate ? this.state.numCorrect : this.state.numCorrect + 1,
      showAnswer: true,     // trigger renderCorrectAnswer
    })
  };

  evaluateAnswer = () => {
    const formatGuess = this.state.guess.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").toLowerCase()
    const answerArray = this.state.currentQuestion.answer.toLowerCase().split(' ');
    return answerArray.includes(formatGuess)
  };

  renderCorrectAnswer(){
    let evaluate =  this.evaluateAnswer();
    return(
      <div className="quiz-play-holder">
        <div className="quiz-question">{this.state.currentQuestion.question}</div>
        <div className={`${evaluate ? 'correct' : 'wrong'}`}>{evaluate ? "You were correct!" : "You were incorrect"}</div>
        <div className="quiz-answer">{this.state.currentQuestion.answer}</div>
        <div className="next-question button" onClick={this.getNextQuestion}> Next Question </div>
      </div>
    )
  }

  restartGame = () => {
    this.setState({
        category: -1,             // selected category
        previousQuestions: [],      // ids of previous questions.
        showAnswer: false,
        categories: [],             // all categories
        numCorrect: 0,
        currentQuestion: null,
        guess: '',
        forceEnd: false,
        questionPerPlay: 5,
    })
  };

  renderPrePlay(){
      return (
          <div className="quiz-play-holder">
              <h3>Choose Category</h3>
                <select name="category" onChange={this.handleChange}>
                  {this.state.categories.map((ca) => (
                      <option
                          key={ca.id}
                          value={ca.id}
                      >{ca.type}
                      </option>
                  ))}
                  <option value='-1' selected>all</option>
                </select>

              <h3>Choose Questions Per Play</h3>
                <select name="questionPerPlay" onChange={this.handleChange}>
                  <option value="5" selected>5</option>
                  <option value="10">10</option>
                  <option value="20">20</option>
                  <option value="50">50</option>
                  <option value="-1">unlimited</option>
                </select>
                <br/><br/>
              <input type="button" className="button" value="Start" onClick={this.getNextQuestion} />
          </div>
      )
  }

  renderFinalScore(){
    return(
      <div className="quiz-play-holder">
        <div className="final-header">
            Your Final Score is:{' '}
            {this.state.numCorrect} out of {this.state.previousQuestions.length}
        </div>
        <div className="play-again button" onClick={this.restartGame}> Play Again? </div>
      </div>
    )
  }



  renderPlay(){
    return this.state.previousQuestions.length === this.state.questionPerPlay || this.state.forceEnd
      ? this.renderFinalScore()
      : this.state.showAnswer
        ? this.renderCorrectAnswer()
        : (
          <div className="quiz-play-holder">
            <div className="quiz-question">{this.state.currentQuestion.question}</div>
            <form onSubmit={this.submitGuess}>
              <input type="text" name="guess" onChange={this.handleChange}/>
              <input className="submit-guess button" type="submit" value="Submit Answer" />
            </form>
          </div>
        )
  }


  render() {
    return this.state.currentQuestion
        ? this.renderPlay()
        : this.renderPrePlay()
  }
}

export default QuizView;

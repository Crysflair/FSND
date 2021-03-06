import React, { Component } from 'react';
import $ from 'jquery';

import '../stylesheets/FormView.css';
import Question from "./Question";

class FormView extends Component {
  constructor(props){
    super();
    this.state = {  // default setting for a new question.
      question: "",
      answer: "",
      difficulty: 1,
      category: 1,
      categories: []  // use `componentDidMount` to load category names.
    }
  }

  componentDidMount(){
    $.ajax({
      url: `/categories`,
      success: (result) => {  // the result should be category names ordered by id.
        this.setState({ categories: result.categories });
        return;
      },
      error: (error) => {
        alert('Unable to load categories. Please try your request again')
        return;
      }
    })
  }


  submitQuestion = (event) => {
    event.preventDefault();
    $.ajax({
      url: '/questions',
      type: "POST",
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify({
        question: this.state.question,
        answer: this.state.answer,
        difficulty: this.state.difficulty,
        category: this.state.category
      }),
      xhrFields: {
        withCredentials: true
      },
      crossDomain: true,
      success: (result) => {
        document.getElementById("add-question-form").reset();
        alert('The question has been added successfully!');
        return;
      },
      error: (error) => {
        alert('Unable to add question. Please try your request again');
        return;
      }
    })
  }

  handleChange = (event) => {
    this.setState({[event.target.name]: event.target.value})
  }

  render() {
    return (
      <div id="add-form">
        <h2>Add a New Trivia Question</h2>
        <form className="form-view" id="add-question-form" onSubmit={this.submitQuestion}>
          <label>
            Question
            <input type="text" name="question" onChange={this.handleChange}/>
          </label>
          <label>
            Answer
            <input type="text" name="answer" onChange={this.handleChange}/>
          </label>
          <label>
            Difficulty
            <select name="difficulty" onChange={this.handleChange}>
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
              <option value="5">5</option>
            </select>
          </label>
          <label>
            Category
            <select name="category" onChange={this.handleChange}>
              {this.state.categories.map((ca) => (
                  <option
                      key={ca.id}
                      value={ca.id}
                  >
                    {ca.type}
                  </option>
              ))}
            </select>
          </label>
          <input type="submit" className="button" value="Submit" />
        </form>
      </div>
    );
  }
}

export default FormView;

import React, { Component } from 'react';

import '../stylesheets/App.css';
import Question from './Question';
import Search from './Search';
import $ from 'jquery';

class QuestionView extends Component {
  constructor(){
    super();
    this.state = {
      questions: [],
      page: 1,
      totalQuestions: 0,
      categories: [],
      currentCategory: null,
      searchTerm: '',
    }
  }

  componentDidMount() {
    this.getQuestions();
  }

  getQuestions = () => {
    $.ajax({
      url: `/categories`,
      type: "GET",
      success: (result) => {
        this.setState({
          categories: result.categories,
        });
        return;
      },
      error: (error) => {
        alert('Unable to load categories. Please try your request again');
        return;
      }
    });
    $.ajax({
      url: `/questions?page=${this.state.page}&current_category=${this.state.currentCategory}&search_term=${this.state.searchTerm}`,
      type: "GET",
      success: (result) => {
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions,
        });
        return;
      },
      error: (error) => {
        alert('Unable to load questions. Please try your request again')
        return;
      }
    });

  };

  selectCategory (id) {
    this.setState({currentCategory: id, page:1}, () => this.getQuestions());
  }

  selectPage(num) {
    this.setState({page: num}, () => this.getQuestions());
  }

  submitSearch = (searchTerm) => {
    this.setState({page: 1, searchTerm: searchTerm}, () => this.getQuestions());
  };

  createPagination(){     // 10 questions per page by default.
    let pageNumbers = [];
    let maxPage = Math.ceil(this.state.totalQuestions / 10);
    for (let i = 1; i <= maxPage; i++) {
      pageNumbers.push(
        <span
          key={i}
          className={`page-num ${i === this.state.page ? 'active' : ''}`}   // if active, use the `active` style.
          onClick={() => {this.selectPage(i)}}>{i}
        </span>)
    }
    return pageNumbers;
  }

  questionAction = (id) => (action) => {
    if(action === 'DELETE') {
      if(window.confirm('are you sure you want to delete the question?')) {
        $.ajax({
          url: `/questions/${id}`, //TODO: update request URL
          type: "DELETE",
          success: (result) => {
            this.getQuestions();
          },
          error: (error) => {
            alert('Unable to load questions. Please try your request again')
            return;
          }
        })
      }
    }
  }

  render() {
    return (
      <div className="question-view">
        <div className="categories-list">
          <h2>Categories</h2>
          <ul>
            {this.state.categories.map((ca) => (
              <li onClick={() => {this.selectCategory(ca.id)}}
                  className={`category ${ca.id === this.state.currentCategory ? 'active' : ''}`}
              >
                {ca.type}
                <img className="category" src={`${ca.type}.svg`}/>
              </li>
            ))}
          </ul>
          <ul>
            <li onClick={() => {this.selectCategory(null)}}
                className={`category ${null === this.state.currentCategory ? 'active' : ''}`}
            >
                Show all categories
                <img className="category" src={`all.svg`}/>
            </li>
          </ul>
          <Search submitSearch={this.submitSearch}/>
        </div>
        <div className="questions-list">
          <h2>Questions</h2>
          {this.state.questions.map((q) => (
            <Question
              key={q.id}
              question={q.question}
              answer={q.answer}
              type={this.state.categories.find(a=>a.id===q.category).type}
              difficulty={q.difficulty}
              questionAction={this.questionAction(q.id)}
            />
          ))}
          <div className="pagination-menu">
            {this.createPagination()}
          </div>
        </div>

      </div>
    );
  }
}

export default QuestionView;

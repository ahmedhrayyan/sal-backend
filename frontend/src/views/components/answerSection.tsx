import React, { useState, useEffect } from "react";
import { connect } from "react-redux";
import { Link } from "react-router-dom";
import Avatar from "./avatar";
import downArrow from "../../images/icons/down-arrow.svg";
import Dropdown from "./dropdown";
import Spinner from "./spinner";
import { selectBestAnswer } from "../../state/ducks/questions/actions";
import { deleteAnswer } from "../../state/ducks/answers/actions";
import { Answer } from "../../state/ducks/answers/types";
import { User } from "../../state/ducks/users/types";

interface AnswerProps {
  answer: Answer;
  users: Map<string, User>;
  currentUser: string;
  bestAnswer: number;
  questionUserId: string;
  selectBestAnswer: any;
  deleteAnswer: any;
  token: string;
}
function AnswerContent({
  answer,
  users,
  currentUser,
  bestAnswer,
  questionUserId,
  selectBestAnswer,
  deleteAnswer,
  token,
}: AnswerProps) {
  function handleReporting() {
    alert("Unfortunately, this action is not implemented yet!");
  }
  function handleUpdating() {
    alert("Unfortunately, this action is not implemented yet!");
  }
  function handleBestAnswer() {
    selectBestAnswer(token, answer.question_id, answer.id);
  }
  function handleDelete() {
    deleteAnswer(token, answer.id);
  }
  let user = users.get(answer.user_id);
  let job = "loading...",
    userName = "loading...";
  if (user) {
    userName = user.user_metadata
      ? user.user_metadata.firstname + " " + user.user_metadata.lastname
      : user.name;
    job = user.user_metadata ? user.user_metadata.job : "software engineer";
    // you've signed in using github :)
  }
  const currentUserAnswer = currentUser === answer.user_id;
  const currentUserQuestion = currentUser === questionUserId;
  const createdAt = new Date(answer.created_at);
  const isBestAnswer = bestAnswer === answer.id;
  return (
    <>
      <div className="card-header">
        <Avatar
          src={user?.picture || ""}
          info={{ name: userName, role: job }}
        />
        <div className="card-header-metadata">
          <p className="content">
            <small>
              {createdAt.toLocaleDateString()}
              <br />
              <span className="text-muted">
                {isBestAnswer ? "Accepted by user" : "Latest answer"}
              </span>
            </small>
          </p>
          <Dropdown
            btnContent={
              <img className="icon" src={downArrow} alt="down-arrow icon" />
            }
          >
            {!currentUserAnswer && (
              <button onClick={handleReporting}>Report this answer</button>
            )}
            {currentUserQuestion && (
              <button onClick={handleBestAnswer}>Select best answer</button>
            )}
            {currentUserAnswer && (
              <button onClick={handleUpdating}>Update answer</button>
            )}
            {currentUserAnswer && (
              <button onClick={handleDelete}>Delete answer</button>
            )}
          </Dropdown>
        </div>
      </div>
      <div className="card-body">
        <p className="card-text">{answer.content}</p>
      </div>
    </>
  );
}
interface Props {
  answer: Answer | undefined;
  users: Map<string, User>;
  token: string;
  currentUser: string;
  bestAnswer: number;
  answerExists: boolean;
  questionId: number;
  questionUserId: string;
  selectBestAnswer: any;
  deleteAnswer: any;
}
function AnswerSection({
  answer,
  users,
  token,
  currentUser,
  bestAnswer,
  answerExists,
  questionId,
  questionUserId,
  selectBestAnswer,
  deleteAnswer,
}: Props) {
  const [formActive, setFormActive] = useState<boolean>(false);
  const [textareaVal, setTextareaVal] = useState<string>("");
  function showForm() {
    setFormActive(true);
  }
  function hideForm() {
    if (textareaVal !== "") {
      const confirm = window.confirm("Discard what you have typed?");
      if (!confirm) {
        return;
      }
    }
    setTextareaVal("");
    setFormActive(false);
  }
  return (
    <div className="card answer">
      {answerExists && !answer && (
        <div className="spinner-container" style={{ height: "60px" }}>
          <Spinner className="spinner-sm spinner-centered" />
        </div>
      )}
      {answer && (
        <AnswerContent
          answer={answer}
          users={users}
          currentUser={currentUser}
          bestAnswer={bestAnswer}
          questionUserId={questionUserId}
          selectBestAnswer={selectBestAnswer}
          token={token}
          deleteAnswer={deleteAnswer}
        />
      )}
      {answerExists && <hr />}
      <div className="answer-cta-section">
        <button className="btn btn-link" onClick={showForm}>
          Write an answer
        </button>
        {answerExists && (
          <Link to={`/${questionId}` || "/"} className="btn btn-link">
            View all answers
          </Link>
        )}
      </div>
      <hr />
      {formActive && (
        <form action="" className="answer-form">
          <div className="form-group">
            <textarea
              name=""
              id=""
              rows={3}
              className="form-control"
              value={textareaVal}
              onChange={(evt) => {
                setTextareaVal(evt.currentTarget.value);
              }}
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Submit
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={hideForm}
          >
            Cancel
          </button>
        </form>
      )}
    </div>
  );
}

function mapStateToProps(state: any) {
  return {
    token: state.auth0.accessToken,
    currentUser: state.auth0.currentUser,
    users: state.users.entities,
  };
}
const mapDispatchToProps = {
  selectBestAnswer,
  deleteAnswer,
};
export default connect(mapStateToProps, mapDispatchToProps)(AnswerSection);

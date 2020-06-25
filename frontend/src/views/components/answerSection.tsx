import React, { useState, FormEvent, useEffect, Fragment } from "react";
import { connect } from "react-redux";
import { Link } from "react-router-dom";
import Avatar from "./avatar";
import downArrow from "../../images/icons/down-arrow.svg";
import Dropdown from "./dropdown";
import Spinner from "./spinner";
import { selectBestAnswer } from "../../state/ducks/questions/actions";
import { deleteAnswer, postAnswer } from "../../state/ducks/answers/actions";
import { Answer } from "../../state/ducks/answers/types";
import { User } from "../../state/ducks/users/types";

interface AnswerProps {
  answer: Answer;
  users: Map<string, User>;
  currentUser: string;
  bestAnswer: number | null;
  questionUserId: string;
  selectBestAnswer: any;
  deleteAnswer: any;
  token: string;
  isUpdatingQuestion: boolean;
}
function AnswerContent(props: AnswerProps) {
  // handle showing the loading logic in the way below
  // is just to only show the loading behavior in only one instance
  const [requestBASent, setRequestBASent] = useState<boolean>(false);
  useEffect(() => {
    if (!props.isUpdatingQuestion) {
      setRequestBASent(false);
    }
  }, [props.isUpdatingQuestion]);
  const [showDropdown, setShowDropdown] = useState<boolean>(false);
  function handleReporting() {
    alert("Unfortunately, this action is not implemented yet!");
  }
  function handleUpdating() {
    alert("Unfortunately, this action is not implemented yet!");
  }
  function handleBestAnswer() {
    props.selectBestAnswer(
      props.answer.question_id,
      props.answer.id,
      props.token
    );
    setRequestBASent(true);
    setShowDropdown(false);
  }
  function handleDelete() {
    props.deleteAnswer(props.answer.id, props.token);
  }
  let user = props.users.get(props.answer.user_id);
  let job = "loading...",
    userName = "loading...";
  if (user) {
    userName = user.user_metadata
      ? user.user_metadata.firstname + " " + user.user_metadata.lastname
      : user.name;
    job = user.user_metadata ? user.user_metadata.job : "software engineer";
    // you've signed in using github :)
  }
  const currentUserAnswer = props.currentUser === props.answer.user_id;
  const currentUserQuestion = props.currentUser === props.questionUserId;
  const createdAt = new Date(props.answer.created_at);
  const isBestAnswer = props.bestAnswer === props.answer.id;
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
                {requestBASent
                  ? "loading..."
                  : isBestAnswer
                  ? "Accepted by user"
                  : "Most recent"}
              </span>
            </small>
          </p>
          <Dropdown
            useDropdown={[showDropdown, setShowDropdown]}
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
        <p className="card-text">{props.answer.content}</p>
      </div>
    </>
  );
}
interface Props {
  users: Map<string, User>;
  token: string;
  currentUser: string;
  bestAnswer: number | null;
  answerExists: boolean;
  questionId: number;
  questionUserId: string;
  selectBestAnswer: any;
  deleteAnswer: any;
  postAnswer: any;
  isUpdatingQuestion: boolean;
  isPostingAnswer: boolean;
  // you must include one of the following properties
  answer?: Answer | undefined;
  answers?: (Answer | undefined)[];
}
function AnswerSection(props: Props) {
  const [formActive, setFormActive] = useState<boolean>(false);
  const [textareaVal, setTextareaVal] = useState<string>("");
  // handle showing the loading logic in the way below
  // is just to only show the loading behavior in only one instance
  const [postingAnswer, setPostingAnswer] = useState<boolean>(false);
  useEffect(() => {
    if (!props.isPostingAnswer) {
      setPostingAnswer(false);
    }
  }, [props.isPostingAnswer]);
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
  function handleSubmit(evt: FormEvent<HTMLFormElement>) {
    evt.preventDefault();
    props.postAnswer(props.questionId, textareaVal, props.token);
    setTextareaVal("");
    setFormActive(false);
    setPostingAnswer(true);
  }

  let answers = null;
  if (props.answers) {
    answers = props.answers.map((answer) => {
      return (
        <Fragment key={Math.random().toString(16).slice(2)}>
          <hr />
          {!answer && (
            <div className="spinner-container" style={{ height: "60px" }}>
              <Spinner className="spinner-sm spinner-centered" />
            </div>
          )}
          {answer && (
            <AnswerContent
              answer={answer}
              users={props.users}
              currentUser={props.currentUser}
              bestAnswer={props.bestAnswer}
              questionUserId={props.questionUserId}
              selectBestAnswer={props.selectBestAnswer}
              token={props.token}
              deleteAnswer={props.deleteAnswer}
              isUpdatingQuestion={props.isUpdatingQuestion}
            />
          )}
        </Fragment>
      );
    });
  }

  return (
    <div className="card answer">
      {/* in case there is only one answer to include */}
      {!answers && (
        <>
          {((!props.answer && props.answerExists) || postingAnswer) && (
            <div className="spinner-container" style={{ height: "60px" }}>
              <Spinner className="spinner-sm spinner-centered" />
            </div>
          )}
          {props.answer && (
            <AnswerContent
              answer={props.answer}
              users={props.users}
              currentUser={props.currentUser}
              bestAnswer={props.bestAnswer}
              questionUserId={props.questionUserId}
              selectBestAnswer={props.selectBestAnswer}
              token={props.token}
              deleteAnswer={props.deleteAnswer}
              isUpdatingQuestion={props.isUpdatingQuestion}
            />
          )}
          {props.answerExists && <hr />}
        </>
      )}
      <div className="answer-cta-section">
        <button className="btn btn-link" onClick={showForm}>
          Write an answer
        </button>
        {props.answerExists && !answers && (
          <Link to={`/questions/${props.questionId}`} className="btn btn-link">
            View all answers
          </Link>
        )}
      </div>
      {formActive && (
        <>
          <hr />
          <form action="" className="answer-form" onSubmit={handleSubmit}>
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
            <button
              type="submit"
              className="btn btn-primary"
              disabled={textareaVal === ""}
            >
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
        </>
      )}
      {/* in case there are multiple answers to include */}
      {answers && (
        <>
          {postingAnswer && (
            <div className="spinner-container" style={{ height: "60px" }}>
              <Spinner className="spinner-sm spinner-centered" />
            </div>
          )}
          {answers}
        </>
      )}
    </div>
  );
}

function mapStateToProps(state: any) {
  return {
    token: state.auth0.accessToken,
    currentUser: state.auth0.currentUser,
    users: state.users.entities,
    isPostingAnswer: state.answers.isPosting,
  };
}
const mapDispatchToProps = {
  selectBestAnswer,
  deleteAnswer,
  postAnswer,
};
export default connect(mapStateToProps, mapDispatchToProps)(AnswerSection);

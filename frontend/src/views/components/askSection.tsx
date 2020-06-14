import React, { CSSProperties } from "react";
import Avatar from "./avatar";
import downArrow from "../../images/icons/down-arrow.svg";
import Dropdown from "./dropdown";
import { Link } from "react-router-dom";
import { Question } from "../../state/ducks/questions/types";
import { deleteQuestion } from "../../state/ducks/questions/actions";
import { User } from "../../state/ducks/users/types";
import { connect } from "react-redux";

interface Props {
  question: Question;
  users: Map<string, User>;
  currentUser: string;
  token: string;
  deleteQuestion: any;
  style?: CSSProperties;
}
function AskSection({
  question,
  users,
  token,
  deleteQuestion,
  currentUser,
  style,
}: Props) {
  let user = users.get(question.user_id);
  let job = "loading...",
    userName = "loading...";
  if (user) {
    userName = user.user_metadata
      ? user.user_metadata.firstname + " " + user.user_metadata.lastname
      : user.name;
    job = user.user_metadata ? user.user_metadata.job : "software engineer"; // you've signed in using github :)
  }
  const currentUserQuestion = currentUser === question.user_id;
  function handleReporting() {
    alert("Unfortunately, this action is not implemented yet!");
  }
  function handleUpdating() {
    alert("Unfortunately, this action is not implemented yet!");
  }
  function handleDeleting() {
    deleteQuestion(token, question.id);
  }
  const createdAt = new Date(question.created_at);
  return (
    <div className="card ask" style={style}>
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
                {question.no_of_answers === 0
                  ? "No answers yet"
                  : question.no_of_answers === 1
                  ? "1 answer"
                  : `${question.no_of_answers} answers`}
              </span>
            </small>
          </p>
          <Dropdown
            btnContent={
              <img className="icon" src={downArrow} alt="down-arrow icon" />
            }
          >
            <Link to={`/${question.id}`}>View question</Link>
            {!currentUserQuestion && (
              <button onClick={handleReporting}>Report this question</button>
            )}
            {currentUserQuestion && (
              <button onClick={handleDeleting}>Delete Question</button>
            )}
            {currentUserQuestion && (
              <button onClick={handleUpdating}>Update Question</button>
            )}
          </Dropdown>
        </div>
      </div>
      <div className="card-body">
        <p className="card-text">{question.content}</p>
      </div>
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
  deleteQuestion,
};
export default connect(mapStateToProps, mapDispatchToProps)(AskSection);

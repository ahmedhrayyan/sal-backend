import React, { FunctionComponent, CSSProperties } from "react";
import Avatar from "./avatar";
import dummyAvatar from "../../images/avatar.jpg";
import downArrow from "../../images/icons/down-arrow.svg";
import Dropdown from "./dropdown";
import { Link } from "react-router-dom";
import { connect } from "react-redux";
import { deleteQuestion } from "../../state/ducks/questions/actions";

interface Props {
  content: string;
  noOfAnswers: number;
  questionId: number;
  questionDate: Date;
  userId: string;
  questionUserId: string;
  deleteQuestion: any;
  token: string;
  style?: CSSProperties;
}

const AskSection: FunctionComponent<Props> = (props) => {
  function handleReporting() {
    alert('Unfortunately, this action is not implemented yet!')
  }
  function handleUpdating() {
    alert('Unfortunately, this action is not implemented yet!')
  }

  function handleDeleting() {
    props.deleteQuestion(props.token, props.questionId)
  }

  // check if the user owns the question
  const isUserQuestion = props.userId === props.questionUserId;

  return (
    <div className="card ask" style={props.style}>
      <div className="card-header">
        <Avatar
          src={dummyAvatar}
          info={{ name: "Mona Kane", role: "Software Engineer" }}
        />
        <div className="card-header-metadata">
          <p className="content">
            <small>
              {props.questionDate.toLocaleDateString()}
              <br />
              <span className="text-muted">
                {props.noOfAnswers === 0
                  ? "No answers yet"
                  : props.noOfAnswers === 1
                  ? "1 answer"
                  : `${props.noOfAnswers} answers`}
              </span>
            </small>
          </p>
          <Dropdown
            btnContent={
              <img className="icon" src={downArrow} alt="down-arrow icon" />
            }
          >
            <Link to={`/${props.questionId}`}>View question</Link>
            <button onClick={handleReporting}>Report this question</button>
            {isUserQuestion && (
              <button onClick={handleDeleting}>Delete Question</button>
            )}
            {isUserQuestion && (
              <button onClick={handleUpdating}>Update Question</button>
            )}
          </Dropdown>
        </div>
      </div>
      <div className="card-body">
        <p className="card-text">{props.content}</p>
      </div>
    </div>
  );
};

const mapDispatchToProps = {
  deleteQuestion
}

export default connect(null, mapDispatchToProps)(AskSection)

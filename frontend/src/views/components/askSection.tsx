import React, { FunctionComponent, CSSProperties } from "react";
import Avatar from "./avatar";
import dummyAvatar from "../../images/avatar.jpg";
import downArrow from "../../images/icons/down-arrow.svg";
import Dropdown from "./dropdown";
import { Link } from "react-router-dom";
import { Question } from "../../state/ducks/questions/types"

interface Props {
  question: Question
  style?: CSSProperties;
}

const AskSection: FunctionComponent<Props> = ({
  question,
  style
}) => {
  function handleReporting() {
    alert('Unfortunately, this action is not implemented yet!')
  }
  function handleUpdating() {
    alert('Unfortunately, this action is not implemented yet!')
  }
  const createdAt = new Date(question.created_at)
  return (
    <div className="card ask" style={style}>
      <div className="card-header">
        <Avatar
          src={dummyAvatar}
          info={{ name: "Mona Kane", role: "Software Engineer" }}
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
            <button onClick={handleReporting}>Report this question</button>
            <button>Delete Question</button>
            <button onClick={handleUpdating}>Update Question</button>
          </Dropdown>
        </div>
      </div>
      <div className="card-body">
        <p className="card-text">{question.content}</p>
      </div>
    </div>
  );
};

export default AskSection

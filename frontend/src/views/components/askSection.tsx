import React, { FunctionComponent, CSSProperties } from "react";
import Avatar from "./avatar";
import dummyAvatar from "../../images/avatar.jpg";
import downArrow from "../../images/icons/down-arrow.svg";
import Dropdown from "./dropdown";

interface Props {
  content: string;
  noOfAnswers: number;
  questionDate: Date;
  style?: CSSProperties
}

const AskSection: FunctionComponent<Props> = (props) => {
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
                  ? 'No answers yet'
                  : props.noOfAnswers === 1
                  ? '1 answer'
                  : `${props.noOfAnswers} answers`
                }
              </span>
            </small>
          </p>
          <Dropdown
            btnContent={
              <img className="icon" src={downArrow} alt="down-arrow icon" />
            }
          >
            <a href="#">item 1</a>
            <a href="#">item 2</a>
          </Dropdown>
        </div>
      </div>
      <div className="card-body">
        <p className="card-text">{props.content}</p>
      </div>
    </div>
  );
};

export default AskSection;

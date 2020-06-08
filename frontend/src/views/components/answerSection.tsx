import React, { FunctionComponent, useState } from "react";
import Avatar from "./avatar";
import dummyAvatar from "../../images/avatar.jpg";
import downArrow from "../../images/icons/down-arrow.svg";
import Dropdown from "./dropdown";

interface Props {}

const AnswerSection: FunctionComponent<Props> = (props) => {
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
      <div className="card-header">
        <Avatar
          src={dummyAvatar}
          info={{ name: "Mona Kane", role: "Software Engineer" }}
        />
        <div className="card-header-metadata">
          <p className="content">
            <small>
              1/6/2020
              <br />
              <span className="text-muted">Accepted by user</span>
            </small>
          </p>
          <Dropdown btnContent={<img className='icon' src={downArrow} alt="down-arrow icon" />}>
            <a href="#">item 1</a>
            <a href="#">item 2</a>
          </Dropdown>
        </div>
      </div>
      <div className="card-body">
        <p className="card-text">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur non
          tellus ac justo mattis mollis. Fusce nec erat at mi tristique gravida.
          Curabitur tempor dui ac ipsum vehicula feugiat. Fusce lacinia tellus
          vel rhoncus commodo. Vivamus efficitur odio ac finibus interdum.
          Praesent hendrerit libero vitae nulla sodales hendrerit.
        </p>
      </div>
      <hr className="card-divider" />
      <div className="answer-cta-section">
        <button className="btn btn-link" onClick={showForm}>
          Write an answer
        </button>
        <button className="btn btn-link">View all answers</button>
      </div>
      <hr className="card-divider" />
      {formActive && (
        <form action="" className="answer-form">
          <textarea
            name=""
            id=""
            rows={3}
            className="form-control form-group"
            value={textareaVal}
            onChange={(evt) => {
              setTextareaVal(evt.currentTarget.value);
            }}
          ></textarea>
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
};

export default AnswerSection;

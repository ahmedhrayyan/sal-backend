import React, { FunctionComponent } from "react";
import Avatar from "./avatar";
import dummyAvatar from "../../images/avatar.jpg";
import downArrow from "../../images/icons/down-arrow.svg";
import Dropdown from "./dropdown";

interface Props {}

const AskSection: FunctionComponent<Props> = (props) => {
  return (
    <div className="card ask">
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
              <span className="text-muted">5 answers</span>
            </small>
          </p>
          <Dropdown btnContent={<img src={downArrow} alt="down-arrow icon" />}>
            <a href="#">item 1</a>
            <a href="#">item 2</a>
          </Dropdown>
        </div>
      </div>
      <div className="card-body">
        <p className="card-text">
          Why are there so many YouTube channels that exploit people who are
          desperate to work for tech companies like Google?
        </p>
      </div>
    </div>
  );
};

export default AskSection;

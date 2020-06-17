import React, { useState, FormEvent } from "react";
import { connect } from "react-redux";
import { postQuestion } from "../../state/ducks/questions/actions";
import { Avatar } from "../components";

interface Props {
  postQuestion: any;
  token: string;
  users: Map<string, any>;
  currentUser: string;
}
function QuestionFrom(props: Props) {
  const [formFocused, setFormFocused] = useState<boolean>(false);
  const [textareaVal, setTextareaVal] = useState<string>("");
  function handleFocus() {
    setFormFocused(true);
  }
  function handleBlur() {
    setFormFocused(false);
  }
  function handleChange(evt: FormEvent<HTMLTextAreaElement>) {
    setTextareaVal(evt.currentTarget.value);
  }
  function handleCancel() {
    setTextareaVal("");
    setFormFocused(false);
  }
  function handleSubmit(evt: FormEvent<HTMLFormElement>) {
    evt.preventDefault();
    props.postQuestion(textareaVal, props.token);
    setTextareaVal("");
    handleBlur();
  }
  const currentUser = props.users.get(props.currentUser);
  return (
    <>
      {formFocused && <div className="q-form-backdrop"></div>}
      <form
        action=""
        onFocus={handleFocus}
        onBlur={handleBlur}
        onSubmit={handleSubmit}
        className={`question-form ${formFocused ? "focus" : ""}`}
        style={{marginTop: '60px'}}
      >
        <div className="backdrop"></div>
        <div className="group">
          <Avatar src={currentUser?.picture || ""} />
          <textarea
            placeholder="Sal about anything..."
            rows={3}
            value={textareaVal}
            onChange={handleChange}
          />
        </div>
        {(formFocused || textareaVal) && (
          <>
            <hr />
            <button
              type="submit"
              className="btn btn-link"
              disabled={textareaVal === ""}
            >
              Submit
            </button>
            <button
              type="button"
              className="btn btn-link"
              onClick={handleCancel}
            >
              Cancel
            </button>
          </>
        )}
      </form>
    </>
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
  postQuestion,
};

export default connect(mapStateToProps, mapDispatchToProps)(QuestionFrom);

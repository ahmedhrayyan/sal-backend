import React, { useState, FormEvent } from "react";
import { connect } from "react-redux";
import { postQuestion } from "../../state/ducks/questions/actions";

interface Props {
  postQuestion: any;
  token: string;
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
    if (textareaVal !== "") {
      const confirm = window.confirm("Discard what you have typed?");
      if (!confirm) {
        return;
      }
    }
    setTextareaVal("");
  }
  function handleSubmit(evt: FormEvent<HTMLFormElement>) {
    evt.preventDefault();
    props.postQuestion(textareaVal, props.token);
    setTextareaVal('')
    handleBlur()
  }
  const btnStyle = {
    marginTop: "10px",
    marginRight: "10px",
  };
  return (
    <form
      action=""
      onFocus={handleFocus}
      onBlur={handleBlur}
      onSubmit={handleSubmit}
    >
      <div className="form-group" style={{ margin: "30px 7px 0" }}>
        <textarea
          placeholder="Your question..."
          className="form-control"
          rows={formFocused ? 3 : 1}
          value={textareaVal}
          onChange={handleChange}
        />
        {(formFocused || textareaVal) && (
          <>
            <button type="submit" className="btn btn-primary" style={btnStyle}>
              Submit
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              style={btnStyle}
              onClick={handleCancel}
            >
              Cancel
            </button>
          </>
        )}
      </div>
    </form>
  );
}

function mapStateToProps(state: any) {
  return {
    token: state.auth0.accessToken,
  };
}

const mapDispatchToProps = {
  postQuestion,
};

export default connect(mapStateToProps, mapDispatchToProps)(QuestionFrom);

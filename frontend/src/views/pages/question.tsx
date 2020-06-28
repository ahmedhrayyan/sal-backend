import React, { useEffect } from "react";
import { useParams, useHistory } from "react-router-dom";
import { connect } from "react-redux";
import { loadQuestion } from "../../state/ducks/questions/actions";
import { Question } from "../../state/ducks/questions/types";
import { loadAnswer } from "../../state/ducks/answers/actions";
import { Answer } from "../../state/ducks/answers/types";
import { QuestionSection, Spinner, AnswerSection } from "../components";

interface Props {
  loadQuestion: any;
  loadAnswer: any;
  questions: Map<number, Question>;
  answers: Map<number, Answer>;
  isUpdatingQuestion: boolean;
}
function QuestionPage(props: Props) {
  const history = useHistory();
  const { questionId } = useParams();
  useEffect(() => {
    props.loadQuestion(parseInt(questionId));
  }, []);

  useEffect(() => {
    const question = props.questions.get(parseInt(questionId));
    if (question) {
      for (const answer_id of question.answers) {
        props.loadAnswer(answer_id);
      }
      document.title = "Sal - " + question.content.slice(0, 24) + "...";
    }
  }, [props.questions]);

  const question = props.questions.get(parseInt(questionId));
  if (!question) {
    return (
      <div className="spinner-container" style={{ height: "180px" }}>
        <Spinner className="spinner-sm spinner-centered" />
      </div>
    );
  }

  const answers = [];
  for (const answer_id of question.answers) {
    if (answer_id === question.best_answer) {
      // show best answer at the begging of answerSection
      answers.unshift(props.answers.get(answer_id));
    } else {
      answers.push(props.answers.get(answer_id));
    }
  }
  return (
    <div className="content-container" style={{ marginBottom: "50px" }}>
      <button
        className="btn btn-link"
        style={{ padding: "14px 5px", color: "#323130" }}
        onClick={() => history.goBack()}
      >
        &lt;&nbsp; Back
      </button>
      <QuestionSection style={{ margin: "0px 5px 0" }} question={question} />
      <AnswerSection
        questionId={question.id}
        questionUserId={question.user_id}
        isUpdatingQuestion={props.isUpdatingQuestion}
        answerExists={question.answers.length > 0}
        bestAnswer={question.best_answer}
        answers={answers}
      />
    </div>
  );
}

function mapStateToProps(state: any) {
  return {
    questions: state.questions.entities,
    isUpdatingQuestion: state.questions.isUpdating,
    answers: state.answers.entities,
  };
}

const mapDispatchToProps = {
  loadQuestion,
  loadAnswer,
};

// export as any due to problem with typescript
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(QuestionPage) as any;

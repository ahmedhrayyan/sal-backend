import React, { useEffect, ReactNode, useRef } from "react";
import { connect } from "react-redux";
import { loadQuestions } from "../../state/ducks/questions/actions";
import { Question } from "../../state/ducks/questions/types";
import { loadUser } from "../../state/ducks/users/actions";
import { User } from "../../state/ducks/users/types";
import { loadAnswer } from "../../state/ducks/answers/actions";
import { QuestionSection } from "../components";
import { AnswerSection } from "../components";
import { Spinner } from "../components";
import { QuestionForm } from "../components";
import { Answer } from "../../state/ducks/answers/types";

interface Props {
  loadQuestions: any;
  questions: Map<number, Question>;
  nextPageUrl: string | null;
  isFetchingQuestions: boolean;
  isPostingQuestion: boolean;
  isUpdatingQuestion: boolean;
  loadUser: any;
  users: Map<number, User>;
  loadAnswer: any;
  answers: Map<number, Answer>;
  currentUser: string; // current user_id
}

function Home(props: Props) {
  const requestedUsers = useRef<Set<string>>(new Set());
  function onAnswerSuccess(response: any) {
    if (!requestedUsers.current.has(response.answer.user_id)) {
      props.loadUser(response.answer.user_id);
      requestedUsers.current.add(response.answer.user_id);
    }
  }
  function onQuestionsSuccess(response: any) {
    for (const question of response.questions) {
      if (!requestedUsers.current.has(question.user_id)) {
        props.loadUser(question.user_id);
        requestedUsers.current.add(question.user_id);
      }
      props.loadAnswer(
        question.best_answer || question.answers[0],
        onAnswerSuccess
      );
    }
  }

  useEffect(() => {
    // if the first page of questions have not been fetched yet
    if (props.questions.size < 10) {
      props.loadQuestions(onQuestionsSuccess);
    }
    document.title = "Sal - The best QA engine?";
  }, []);

  function handleFetchNewQuestions() {
    props.loadQuestions(onQuestionsSuccess)
  }

  let QAComponents: ReactNode[] = [];
  for (const question of props.questions.values()) {
    QAComponents.push(
      <div key={question.id}>
        <QuestionSection
          key={question.id}
          style={{ margin: "50px 5px 0" }}
          question={question}
        />
        <AnswerSection
          bestAnswer={question.best_answer}
          answerExists={question.answers.length > 0}
          answer={props.answers.get(
            question.best_answer || question.answers[0]
          )}
          questionId={question.id}
          questionUserId={question.user_id}
          isUpdatingQuestion={props.isUpdatingQuestion}
        />
      </div>
    );
  }
  // homepage top spinner condition
  const condition =
    (props.isFetchingQuestions && props.questions.size === 0) ||
    props.isPostingQuestion;
  return (
    <div className="content-container" style={{ marginBottom: "50px" }}>
      <QuestionForm style={{ marginTop: "50px" }} />
      {/* show spinner on homepage top */}
      {condition && (
        <div className="spinner-container" style={{ height: "180px" }}>
          <Spinner className="spinner-sm spinner-centered" />
        </div>
      )}
      {QAComponents}
      {props.nextPageUrl && (
        <div
          style={{ textAlign: "center", marginTop: "30px" }}
          onClick={handleFetchNewQuestions}
        >
          <button className="btn btn-link">Load More</button>
        </div>
      )}
    </div>
  );
}

function mapStateToProps(state: any) {
  return {
    currentUser: state.auth0.currentUser,
    questions: state.questions.entities,
    nextPageUrl: state.questions.nextPageUrl,
    isFetchingQuestions: state.questions.isFetching,
    isPostingQuestion: state.questions.isPosting,
    isUpdatingQuestion: state.questions.isUpdating,
    users: state.users.entities,
    answers: state.answers.entities,
  };
}
const mapDispatchToProps = {
  loadQuestions,
  loadUser,
  loadAnswer,
};
export default connect(mapStateToProps, mapDispatchToProps)(Home);

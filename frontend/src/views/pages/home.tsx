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
  useEffect(() => {
    // if there is not question
    if (!props.questions.size) {
      props.loadQuestions();
    }
  }, []);
  const requestedUsers = useRef<Set<string>>(new Set());
  useEffect(() => {
    for (const question of props.questions.values()) {
      // do not make multiple requests with the same id
      // we've requested the current user in in App component
      if (
        !requestedUsers.current.has(question.user_id) &&
        question.user_id !== props.currentUser
      ) {
        props.loadUser(question.user_id);
        requestedUsers.current.add(question.user_id);
      }
      // fetch answers
      props.loadAnswer(question.best_answer || question.latest_answer);
    }
  }, [props.questions]);

  useEffect(() => {
    for (const answer of props.answers.values()) {
      if (
        !requestedUsers.current.has(answer.user_id) &&
        answer.user_id !== props.currentUser
      ) {
        props.loadUser(answer.user_id);
        requestedUsers.current.add(answer.user_id);
      }
    }
  }, [props.answers]);

  let QAComponents: ReactNode[] = [];
  for (const question of props.questions.values()) {
    QAComponents.push(
      <div key={question.id}>
        <QuestionSection
          key={question.id}
          style={{ margin: "60px 7px 0" }}
          question={question}
        />
        <AnswerSection
          bestAnswer={question.best_answer}
          answerExists={question.no_of_answers > 0}
          answer={props.answers.get(
            question.best_answer as number || question.latest_answer as number
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
    <div className="content-container">
      <QuestionForm />
      {/* show spinner on homepage top */}
      {condition && (
        <div className="spinner-container" style={{ height: "180px" }}>
          <Spinner className="spinner-sm spinner-centered" />
        </div>
      )}
      {QAComponents}
    </div>
  );
}

function mapStateToProps(state: any) {
  return {
    currentUser: state.auth0.currentUser,
    questions: state.questions.entities,
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

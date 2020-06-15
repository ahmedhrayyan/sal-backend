import React, {
  useEffect,
  ReactNode,
  Fragment,
  useState,
  useRef,
  FormEvent,
} from "react";
import { connect } from "react-redux";
import { loadQuestions } from "../../state/ducks/questions/actions";
import { Question } from "../../state/ducks/questions/types";
import { loadUser } from "../../state/ducks/users/actions";
import { User } from "../../state/ducks/users/types";
import { loadAnswer } from "../../state/ducks/answers/actions";
import { AskSection } from "../components";
import { AnswerSection } from "../components";
import { Spinner } from "../components";
import { QuestionForm } from "../components";
import { Answer } from "../../state/ducks/answers/types";
import { answers } from "../../state/ducks";

interface Props {
  token: string;
  loadQuestions: any;
  questions: Map<number, Question>;
  fetchingQuestions: boolean;
  loadUser: any;
  users: Map<number, User>;
  loadAnswer: any;
  answers: Map<number, Answer>;
  fetchingUser: boolean;
}

function Home(props: Props) {
  useEffect(() => {
    // if there is not question
    if (!props.questions.size) {
      props.loadQuestions(props.token);
    }
  }, []);
  const usersToBeFetched = useRef<Set<string>>(new Set());
  useEffect(() => {
    for (const question of props.questions.values()) {
      // do not make multiple requests with the same id
      usersToBeFetched.current.add(question.user_id)
      // fetch answers
      props.loadAnswer(
        props.token,
        question.best_answer || question.latest_answer
      )
    }
    for (const user_id of usersToBeFetched.current) {
      props.loadUser(props.token, user_id)
    }
  }, [props.questions]);

  useEffect(() => {
    for (const answer of props.answers.values()) {
      // load answer author if he hasn't been called above
      if (!usersToBeFetched.current.has(answer.user_id)) {
        props.loadUser(answer.user_id)
      }
    }
  }, [props.answers]);

  let QAComponents: ReactNode[] = [];
  for (const question of props.questions.values()) {
    QAComponents.push(
      <div key={question.id}>
        <AskSection
          key={question.id}
          style={{ margin: "60px 7px 0" }}
          question={question}
        />
        <AnswerSection
          bestAnswer={question.best_answer}
          answerExists={question.no_of_answers > 0}
          answer={props.answers.get(
            question.best_answer || question.latest_answer
          )}
          questionId={question.id}
          questionUserId={question.user_id}
        />
      </div>
    );
  }
  return (
    <div className="content-container">
      <QuestionForm />
      {props.fetchingQuestions && props.questions.size === 0 && (
        <div className="spinner-container" style={{ height: "120px" }}>
          <Spinner className="spinner-sm spinner-centered" />
        </div>
      )}
      {QAComponents}
    </div>
  );
}

function mapStateToProps(state: any) {
  return {
    token: state.auth0.accessToken,
    questions: state.questions.entities,
    fetchingQuestions: state.questions.isFetching,
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

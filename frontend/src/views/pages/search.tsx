import React, { ReactNode, useEffect, useRef } from "react";
import { connect } from "react-redux";
import { useLocation, Link } from "react-router-dom";
import { Spinner, QuestionSection } from "../components";
import { loadSearch } from "../../state/ducks/search/actions";
import { loadUser } from "../../state/ducks/users/actions";

interface Props {
  questions: Map<number, any>;
  isFetchingQuestions: boolean;
  nextPageUrl: string;
  loadSearch: any;
  loadUser: any;
  currentUser: string;
}
function SearchPage(props: Props) {
  const { search } = useLocation();
  const params = new URLSearchParams(search);
  useEffect(() => {
    if (params.get("term")) {
      props.loadSearch(params.get("term"));
      document.title = "Sal - search for " + params.get("term")
    }
  }, [search]);

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
    }
  }, [props.questions]);

  if (!params.get("term")) {
    return (
      <div className="content-container">
        <h1>You've searched for nothing!</h1>
      </div>
    );
  }

  function handleFetchNewQuestions() {
    props.loadSearch(params.get("term"));
  }

  let QComponents: ReactNode[] = [];
  for (const question of props.questions.values()) {
    QComponents.push(
      <div key={question.id}>
        <QuestionSection
          key={question.id}
          style={{ margin: "50px 5px 0" }}
          question={question}
        />
        <div className="card answer">
          <div className="answer-cta-section">
            <Link to={`/questions/${question.id}`} className="btn btn-link">
              View Question
            </Link>
          </div>
        </div>
      </div>
    );
  }
  // search top spinner condition
  const condition = props.isFetchingQuestions && props.questions.size === 0;
  return (
    <div className="content-container" style={{ marginBottom: "50px" }}>
      {/* show spinner on search page */}
      {condition && (
        <div className="spinner-container" style={{ height: "180px" }}>
          <Spinner className="spinner-sm spinner-centered" />
        </div>
      )}
      {QComponents}
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
    questions: state.search.entities,
    isFetchingQuestions: state.search.isFetching,
    nextPageUrl: state.search.nextPageUrl,
  };
}
const mapDispatchToProps = {
  loadSearch,
  loadUser,
};
export default connect(mapStateToProps, mapDispatchToProps)(SearchPage);

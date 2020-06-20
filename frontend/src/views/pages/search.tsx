import React, { ReactNode, useEffect } from "react";
import { connect } from "react-redux";
import { useLocation, Link } from "react-router-dom";
import { Spinner, QuestionSection, AnswerSection } from "../components";
import { loadSearch } from "../../state/ducks/search/actions";

interface Props {
  questions: Map<number, any>;
  isFetchingQuestions: boolean;
  nextPageUrl: string;
  loadSearch: any;
}
function SearchPage(props: Props) {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  useEffect(() => {
    if (params.get('term') && !props.questions.size) {
      props.loadSearch(params.get('term'))
    }
  }, [params])

  if (!params.get('term')) {
    return (
      <div className="content-container">
        <h1>You've searched for nothing!</h1>
      </div>
    );
  }

  function handleFetchNewQuestions() {
    props.loadSearch(params.get('term'))
  }

  let QComponents: ReactNode[] = [];
  for (const question of props.questions.values()) {
    QComponents.push(
      <div key={question.id}>
        <QuestionSection
          key={question.id}
          style={{ margin: "50px 7px 0" }}
          question={question}
        />
        <div className="card answer">
          <div className="answer-cta-section">
            <Link to={`/questions/${question.id}`} className="btn btn-link">View Question</Link>
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
    questions: state.search.entities,
    isFetchingQuestions: state.search.isFetching,
    nextPageUrl: state.search.nextPageUrl,
  };
}
const mapDispatchToProps = {
  loadSearch
};
export default connect(mapStateToProps, mapDispatchToProps)(SearchPage);

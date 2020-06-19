import React from "react"
import { useParams } from "react-router-dom";
import { connect } from "react-redux";

interface Props {
}
function QuestionPage(props: Props) {
  const { questionId } = useParams();
  return <h1>You've request question {questionId}</h1>
}

export default connect(null, null)(QuestionPage);

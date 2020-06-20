import React from "react";
import { useLocation } from "react-router-dom";

interface Props {}
function SearchPage(props: Props) {
  const location = useLocation();
  const params = new URLSearchParams(location.search);

  if (!location.search) {
    return (
      <h1>You've searched for nothing!</h1>
    )
  }

  return <h1>You've searched for {params.get("question")}</h1>;
}

export default SearchPage;

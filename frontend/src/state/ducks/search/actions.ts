import { Types } from "./types";
import { CALL_API } from "../../middlewares/apiService";

// load questions by page
function searchQuestions(search: string, nextPageUrl: string) {
  return {
    [CALL_API]: {
      endpoint: nextPageUrl,
      types: [Types.SEARCH_REQUEST, Types.SEARCH_SUCCESS, Types.SEARCH_FAILURE],
      config: {
        method: "POST",
        body: JSON.stringify({
          search: search,
        }),
        headers: {
          "Content-Type": "application/json",
        },
      },
    },
  };
}

export function loadSearch(search: string) {
  return function (dispatch: any, getState: any) {
    const { searchTerm, nextPageUrl = "/api/search", pageCount = 0 } =
      getState().search || {};

    // searchTerm have changed
    if (searchTerm !== null && searchTerm !== search) {
      return dispatch(searchQuestions(search, '/api/search'))
    }
    // don't make pointless requests
    if (pageCount > 0 && !nextPageUrl) {
      return null;
    }
    // initial call
    return dispatch(searchQuestions(search, nextPageUrl));
  };
}

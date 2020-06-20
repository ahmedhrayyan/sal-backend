import { Types, Question } from "./types";
const defaultState = {
  isFetching: false,
  errorMessage: null,
  searchTerm: null,
  pageCount: 0, // we haven't fetched any page yet
  entities: new Map<number, Question>(),
};

function searchReducer(state = defaultState, action: any) {
  switch (action.type) {
    case Types.SEARCH_REQUEST:
      return Object.assign({}, state, {
        isFetching: true,
      });
    case Types.SEARCH_SUCCESS: {
      let newEntities;
      // searchTerm have changed
      if (state.searchTerm && state.searchTerm !== action.payload.search_term) {
        newEntities = new Map(); // clear old entities
      } else {
        newEntities = new Map(state.entities); // clone old questions
      }
      for (const entity of action.payload.questions) {
        newEntities.set(entity.id, entity);
      }
      return Object.assign({}, state, {
        isFetching: false,
        entities: newEntities,
        nextPageUrl: action.payload.next_path,
        noOfQuestions: action.payload.no_of_questions,
        lastUpdated: action.receivedAt,
        pageCount: state.pageCount + 1,
        searchTerm: action.payload.search_term
      });
    }
    case Types.SEARCH_FAILURE:
      return Object.assign({}, state, {
        errorMessage: action.error,
        isFetching: false,
      });
    default:
      return state;
  }
}

export default searchReducer;

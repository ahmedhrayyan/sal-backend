import { Types, Answer } from "./types";
const defaultState = {
  isFetching: false,
  errorMessage: null,
  entities: new Map<number, Answer>(),
};

function answersReducer(state = defaultState, action: any) {
  switch (action.type) {
    case Types.ANSWER_REQUEST:
      return Object.assign({}, state, {
        isFetching: true,
      });
    case Types.ANSWER_SUCCESS: {
      let newEntities = new Map(state.entities); // clone old questions
      newEntities.set(action.payload.answer.id, action.payload.answer);
      return Object.assign({}, state, {
        isFetching: false,
        entities: newEntities,
        lastUpdated: action.receivedAt,
      });
    }
    case Types.ANSWER_FAILURE:
      return Object.assign({}, state, {
        errorMessage: action.error,
        isFetching: false,
      });
    default:
      return state;
  }
}

export default answersReducer;

import { Types, User } from "./types";
const defaultState = {
  isFetching: false,
  errorMessage: null,
  entities: new Map<string, User>(),
};

function questionsReducer(state = defaultState, action: any) {
  switch (action.type) {
    case Types.USER_REQUEST:
      return Object.assign({}, state, {
        isFetching: true,
      });
    case Types.USER_SUCCESS: {
      let newEntities = new Map(state.entities); // clone old questions
      newEntities.set(action.payload.user.user_id, action.payload.user)
      return Object.assign({}, state, {
        isFetching: false,
        entities: newEntities,
        lastUpdated: action.receivedAt,
      });
    }
    case Types.USER_FAILURE:
      return Object.assign({}, state, {
        errorMessage: action.error,
        isFetching: false,
      });
    default:
      return state;
  }
}

export default questionsReducer;

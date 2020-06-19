import { Types, Answer } from "./types";
const defaultState = {
  isFetching: false,
  isPosting: false,
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
    case Types.A_DELETE_REQUEST:
      return Object.assign({}, state, {
        isFetching: true,
      });
    case Types.A_DELETE_SUCCESS: {
      const newEntities = new Map(state.entities);
      newEntities.delete(action.payload.del_id);
      return Object.assign({}, state, {
        entities: newEntities,
        isFetching: false,
      });
    }
    case Types.A_DELETE_FAILURE:
      return Object.assign({}, state, {
        isFetching: false,
        errorMessage: action.error,
      });
    case Types.A_POST_REQUEST:
      return Object.assign({}, state, {
        isPosting: true,
      });
    case Types.A_POST_SUCCESS: {
      const newEntities = new Map([
        [action.payload.created.id, action.payload.created],
        ...state.entities,
      ]);
      return Object.assign({}, state, {
        isPosting: false,
        entities: newEntities,
      });
    }
    case Types.A_POST_FAILURE:
      return Object.assign({}, state, {
        isPosting: false,
        errorMessage: action.error,
      });
    default:
      return state;
  }
}

export default answersReducer;

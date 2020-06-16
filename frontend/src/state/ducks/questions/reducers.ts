import { Types, Question } from "./types";
const defaultState = {
  isFetching: false,
  errorMessage: null,
  pageCount: 0, // we haven't fetched any page yet
  entities: new Map<number, Question>(),
};

function questionsReducer(state = defaultState, action: any) {
  switch (action.type) {
    case Types.QUESTIONS_REQUEST:
      return Object.assign({}, state, {
        isFetching: true,
      });
    case Types.QUESTIONS_SUCCESS: {
      let newEntities = new Map(state.entities); // clone old questions
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
      });
    }
    case Types.QUESTIONS_FAILURE:
      return Object.assign({}, state, {
        errorMessage: action.error,
        isFetching: false,
      });
    case Types.Q_DELETE_REQUEST:
      return Object.assign({}, state, {
        isFetching: true,
      });
    case Types.Q_DELETE_SUCCESS: {
      const newEntities = new Map(state.entities);
      newEntities.delete(action.payload.del_id);
      return Object.assign({}, state, {
        entities: newEntities,
        isFetching: false,
      });
    }
    case Types.Q_DELETE_FAILURE:
      return Object.assign({}, state, {
        isFetching: false,
        errorMessage: action.error,
      });

    case Types.Q_POST_REQUEST:
      return Object.assign({}, state, {
        isFetching: true,
      });
    case Types.Q_POST_SUCCESS: {
      const newEntities = new Map([
        [action.payload.created.id, action.payload.created],
        ...state.entities,
      ]);
      return Object.assign({}, state, {
        isFetching: false,
        entities: newEntities,
      });
    }
    case Types.Q_POST_FAILURE:
      return Object.assign({}, state, {
        isFetching: false,
        errorMessage: action.error,
      });
    case Types.Q_BA_REQUEST:
      return Object.assign({}, state, {
        isFetching: true,
      });
    case Types.Q_BA_SUCCESS: {
      const newEntities = new Map(state.entities);
      newEntities.set(action.payload.patched.id, action.payload.patched);
      return Object.assign({}, state, {
        isFetching: false,
        entities: newEntities
      });
    }
    case Types.Q_BA_FAILURE: {
      return Object.assign({}, state, {
        isFetching: false,
        errorMessage: action.error
      });
    }

    default:
      return state;
  }
}

export default questionsReducer;

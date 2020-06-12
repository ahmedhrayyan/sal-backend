import { Types } from "./types";
const defaultState = {
  isFetching: false,
  errorMessage: null,
  lastUpdated: null,
  fetchedPageCount: 0, // we did not fetch any pages yet
  noOfQuestions: null,
  entities: new Map<number, any>(),
};

function questionsReducer(state = defaultState, action: any) {
  switch (action.type) {
    case Types.QUESTIONS_REQUEST:
      return Object.assign({}, state, {
        isFetching: true,
      });
    case Types.QUESTIONS_SUCCESS: {
      // make sure we have fetched a whole page (10 questions per page)
      // otherwise do not increase the fetchedPageCount
      const noOfNewEntities = action.payload.questions.length;
      const fetchedPageCount =
        noOfNewEntities < 10
          ? state.fetchedPageCount
          : state.fetchedPageCount + 1;

      let newEntities = new Map(state.entities); // clone old questions
      for (const entity of action.payload.questions) {
        newEntities.set(entity.id, entity);
      }
      return Object.assign({}, state, {
        isFetching: false,
        entities: newEntities,
        fetchedPageCount,
        noOfQuestions: action.payload.no_of_questions,
        lastUpdated: action.receivedAt,
      });
    }
    case Types.QUESTIONS_FAILURE:
      return Object.assign({}, state, {
        errorMessage: action.error,
        isFetching: false,
      });
    case Types.Q_DELETE_REQUEST:
      return Object.assign({}, state, {
        isFetching: true
      })
    case Types.Q_DELETE_SUCCESS: {
      const newEntities = new Map(state.entities)
      newEntities.delete(action.payload.del_id)
      return Object.assign({}, state, {
        entities: newEntities,
        isFetching: false
      })
    }
    case Types.Q_DELETE_FAILURE:
      return Object.assign({}, state, {
        isFetching: false,
        errorMessage: action.error
      })

    default:
      return state;
  }
}

export default questionsReducer;

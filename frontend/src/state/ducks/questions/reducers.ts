import { Types, Question } from "./types";
import { Types as AnswersTypes } from "../answers/types";
const defaultState = {
  isFetching: false,
  isPosting: false,
  isUpdating: false,
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
    case Types.QUESTION_REQUEST:
      return Object.assign({}, state, {
        isFetching: true,
      });
    case Types.QUESTION_SUCCESS: {
      let newEntities = new Map(state.entities); // clone old questions
      newEntities.set(action.payload.question.id, action.payload.question);
      return Object.assign({}, state, {
        isFetching: false,
        entities: newEntities,
        lastUpdated: action.receivedAt,
      });
    }
    case Types.QUESTION_FAILURE:
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
        isPosting: true,
      });
    case Types.Q_POST_SUCCESS: {
      const newEntities = new Map([
        [action.payload.created.id, action.payload.created],
        ...state.entities,
      ]);
      return Object.assign({}, state, {
        isPosting: false,
        entities: newEntities,
      });
    }
    case Types.Q_POST_FAILURE:
      return Object.assign({}, state, {
        isPosting: false,
        errorMessage: action.error,
      });
    case Types.Q_BA_REQUEST:
      return Object.assign({}, state, {
        isUpdating: true,
      });
    case Types.Q_BA_SUCCESS: {
      const newEntities = new Map(state.entities);
      newEntities.set(action.payload.patched.id, action.payload.patched);
      return Object.assign({}, state, {
        isUpdating: false,
        entities: newEntities,
      });
    }
    case Types.Q_BA_FAILURE: {
      return Object.assign({}, state, {
        isUpdating: false,
        errorMessage: action.error,
      });
    }

    // Update questions based on answers types
    case AnswersTypes.A_DELETE_SUCCESS: {
      const newEntities = new Map(state.entities);
      const question = newEntities.get(action.payload.question_id) as Question;
      // remove deleted id from question answers array
      question.answers = question.answers.filter(
        (id) => id !== action.payload.del_id
      );
      if (question.best_answer === action.payload.del_id) {
        question.best_answer = null;
      }
      return Object.assign({
        entities: newEntities,
      });
    }

    case AnswersTypes.A_POST_SUCCESS: {
      const newEntities = new Map(state.entities);
      const question = newEntities.get(
        action.payload.created.question_id
      ) as Question;
      // add the created id to the first of the question answers array
      question.answers.unshift(action.payload.created.id);
      return Object.assign({
        entities: newEntities,
      });
    }

    default:
      return state;
  }
}

export default questionsReducer;

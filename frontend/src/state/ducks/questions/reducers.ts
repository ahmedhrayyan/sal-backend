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
      // yes I know I shouldn't mutate the state directly,
      // but it's sometimes fun to break the rules :)
      const question = state.entities.get(
        action.payload.question_id
      ) as Question;
      question.no_of_answers -= 1;
      if (question.best_answer === action.payload.del_id) {
        question.best_answer = null;
      }
      if (question.latest_answer === action.payload.del_id) {
        // this line of code is bad because the question probably
        // has more than one answer, but I'll leave it as it is for now
        question.latest_answer = null;
      }
      return state;
    }

    case AnswersTypes.A_POST_SUCCESS: {
      const question = state.entities.get(
        action.payload.created.question_id
      ) as Question;
      question.no_of_answers += 1;
      // if question doesn't have best answer
      // set question latest answer to the new created answer
      if (!question.best_answer) {
        question.latest_answer = action.payload.created.id;
      }
      return state;
    }

    default:
      return state;
  }
}

export default questionsReducer;

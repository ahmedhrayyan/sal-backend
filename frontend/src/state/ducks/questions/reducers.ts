import { Types } from "./types";
const defaultState = {
  isFetching: false,
  errorMessage: null,
  lastUpdated: null,
  questions: new Map<number, any>()
}

function questionsReducer(state = defaultState, action: any) {
  switch (action.type) {
    case Types.QUESTIONS_REQUEST:
      return Object.assign({}, state, {
        isFetching: true
      })
    case Types.QUESTIONS_SUCCESS: {
      let newQuestions = new Map(state.questions) // clone old questions
      for (const question of action.payload.questions) {
        newQuestions.set(question.id, question)
      }
      return Object.assign({}, state, {
        isFetching: false,
        questions: newQuestions,
        lastUpdated: action.receivedAt
      })
    }
    case Types.QUESTIONS_FAILURE:
      return Object.assign({}, state, {
        errorMessage: action.error,
        isFetching: false
      })
    default:
      return state
  }
}

export default questionsReducer

import { Types } from "./types";
import { CALL_API } from "../../middlewares/apiService"

export function fetchQuestions(token: string, pageCount: number | string) {
  return {
    [CALL_API]: {
      endpoint: `/questions?page=${pageCount}`,
      token: token,
      types: [
        Types.QUESTIONS_REQUEST,
        Types.QUESTIONS_SUCCESS,
        Types.QUESTIONS_FAILURE
      ]
    }
  }
}

export function deleteQuestion(token: string, id: number | string) {
  return {
    [CALL_API]: {
      endpoint: `/questions/${id}`,
      token: token,
      method: 'DELETE',
      types: [
        Types.Q_DELETE_REQUEST,
        Types.Q_DELETE_SUCCESS,
        Types.Q_DELETE_FAILURE
      ]
    }
  }
}

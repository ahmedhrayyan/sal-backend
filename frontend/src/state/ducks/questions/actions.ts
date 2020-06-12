import { Types } from "./types";
import { CALL_API } from "../../middlewares/apiService"

export function fetchQuestions(token: string) {
  return {
    [CALL_API]: {
      endpoint: '/questions',
      token: token,
      types: [
        Types.QUESTIONS_REQUEST,
        Types.QUESTIONS_SUCCESS,
        Types.QUESTIONS_FAILURE
      ]
    }
  }
}

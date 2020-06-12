import { Types } from "./types";
import { CALL_API } from "../../middlewares/apiService"

export function fetchQuestions(token: string, pageCount: number) {
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

import { Types } from "./types";
import { CALL_API } from "../../middlewares/apiService";

function fetchAnswer(id: string) {
  return {
    [CALL_API]: {
      endpoint: `/api/answers/${id}`,
      types: [
        Types.ANSWER_REQUEST,
        Types.ANSWER_SUCCESS,
        Types.ANSWER_FAILURE
      ],
    },
  };
}

export function loadAnswer(id: string) {
  return function (dispatch: any, getState: any) {
    const answer = getState().answers.entities.get(id);
    // do not send pointless requests
    if (answer || !id) {
      return null;
    }
    return dispatch(fetchAnswer(id));
  };
}

export function deleteAnswer(id: string, token: string) {
  return {
    [CALL_API]: {
      endpoint: `/api/answers/${id}`,
      token: token,
      types: [
        Types.A_DELETE_REQUEST,
        Types.A_DELETE_SUCCESS,
        Types.ANSWER_FAILURE
      ],
      config: {
        method: 'DELETE'
      }
    },
  };
}

export function postAnswer(questionId: number, content: string, token: string,) {
  return {
    [CALL_API]: {
      endpoint: `/api/questions/${questionId}/answers`,
      token: token,
      types: [
        Types.A_POST_REQUEST,
        Types.A_POST_SUCCESS,
        Types.A_POST_FAILURE,
      ],
      config: {
        method: 'POST',
        body: JSON.stringify({content}),
        headers: {
          'Content-Type': 'application/json'
        }
      }
    }
  }
}

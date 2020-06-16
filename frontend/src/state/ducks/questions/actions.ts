import { Types } from "./types";
import { CALL_API } from "../../middlewares/apiService";

function fetchQuestions(token: string, nextPageUrl: string) {
  return {
    [CALL_API]: {
      endpoint: nextPageUrl,
      token: token,
      types: [
        Types.QUESTIONS_REQUEST,
        Types.QUESTIONS_SUCCESS,
        Types.QUESTIONS_FAILURE,
      ],
    },
  };
}

export function loadQuestions(token: string) {
  return function (dispatch: any, getState: any) {
    const { nextPageUrl = "/api/questions", pageCount = 0 } =
      getState().questions || {};
    // don't make pointless requests
    if (pageCount > 0 && !nextPageUrl) {
      return;
    }
    return dispatch(fetchQuestions(token, nextPageUrl));
  };
}

export function deleteQuestion(token: string, id: number) {
  if (!id) {
    // don't send pointless requests
    return null
  }
  return {
    [CALL_API]: {
      endpoint: `/api/questions/${id}`,
      token: token,
      types: [
        Types.Q_DELETE_REQUEST,
        Types.Q_DELETE_SUCCESS,
        Types.Q_DELETE_FAILURE,
      ],
      config: {
        method: 'DELETE'
      }
    },
  };
}

export function postQuestion(token: string, content: string) {
  return {
    [CALL_API]: {
      endpoint: '/api/questions',
      token: token,
      types: [
        Types.Q_POST_REQUEST,
        Types.Q_POST_SUCCESS,
        Types.Q_POST_FAILURE,
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

export function selectBestAnswer(token: string, question_id: number, answer_id: number) {
  return {
    [CALL_API]: {
      endpoint: `/api/questions/${question_id}`,
      token: token,
      types: [
        Types.Q_BA_REQUEST,
        Types.Q_BA_SUCCESS,
        Types.Q_BA_FAILURE,
      ],
      config: {
        method: 'PATCH',
        body: JSON.stringify({answer: answer_id}),
        headers: {
          'Content-Type': 'application/json'
        }
      }
    }
  }
}

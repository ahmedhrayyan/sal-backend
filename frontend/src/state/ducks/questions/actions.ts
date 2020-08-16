import { Types } from "./types";
import { CALL_API } from "../../middlewares/apiService";

// load questions by page
function fetchQuestions(
  nextPageUrl: string,
  onSuccess: Function | null,
  onFailure: Function | null
) {
  return {
    [CALL_API]: {
      endpoint: nextPageUrl,
      onSuccess,
      onFailure,
      types: [
        Types.QUESTIONS_REQUEST,
        Types.QUESTIONS_SUCCESS,
        Types.QUESTIONS_FAILURE,
      ],
    },
  };
}

export function loadQuestions(
  onSuccess: Function | null = null,
  onFailure: Function | null = null
) {
  return function (dispatch: any, getState: any) {
    const { nextPageUrl = "/api/questions", pageCount = 0 } =
      getState().questions || {};
    // don't make pointless requests
    if (pageCount > 0 && !nextPageUrl) {
      return;
    }
    return dispatch(fetchQuestions(nextPageUrl, onSuccess, onFailure));
  };
}

// load only one question
function fetchQuestion(id: string) {
  return {
    [CALL_API]: {
      endpoint: `/api/questions/${id}`,
      types: [
        Types.QUESTION_REQUEST,
        Types.QUESTION_SUCCESS,
        Types.QUESTION_FAILURE,
      ],
    },
  };
}

export function loadQuestion(id: string) {
  return function (dispatch: any, getState: any) {
    const answer = getState().questions.entities.get(id);
    // do not send pointless requests
    if (answer || !id) {
      return null;
    }
    return dispatch(fetchQuestion(id));
  };
}

export function deleteQuestion(id: number, token: string) {
  if (!id) {
    // don't send pointless requests
    return null;
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
        method: "DELETE",
      },
    },
  };
}

export function postQuestion(content: string, token: string) {
  return {
    [CALL_API]: {
      endpoint: "/api/questions",
      token: token,
      types: [Types.Q_POST_REQUEST, Types.Q_POST_SUCCESS, Types.Q_POST_FAILURE],
      config: {
        method: "POST",
        body: JSON.stringify({ content }),
        headers: {
          "Content-Type": "application/json",
        },
      },
    },
  };
}

export function selectBestAnswer(
  question_id: number,
  answer_id: number,
  token: string
) {
  return {
    [CALL_API]: {
      endpoint: `/api/questions/${question_id}`,
      token: token,
      types: [Types.Q_BA_REQUEST, Types.Q_BA_SUCCESS, Types.Q_BA_FAILURE],
      config: {
        method: "PATCH",
        body: JSON.stringify({ answer: answer_id }),
        headers: {
          "Content-Type": "application/json",
        },
      },
    },
  };
}

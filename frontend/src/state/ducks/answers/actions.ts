import { Types } from "./types";
import { CALL_API } from "../../middlewares/apiService";

function fetchAnswer(token: string, id: string) {
  return {
    [CALL_API]: {
      endpoint: `/api/answers/${id}`,
      token: token,
      types: [
        Types.ANSWER_REQUEST,
        Types.ANSWER_SUCCESS,
        Types.ANSWER_FAILURE
      ],
    },
  };
}

export function loadAnswer(token: string, id: string) {
  return function (dispatch: any, getState: any) {
    const answer = getState().answers.entities.get(id);
    // do not send pointless requests
    if (answer || !id) {
      return null;
    }
    return dispatch(fetchAnswer(token, id));
  };
}

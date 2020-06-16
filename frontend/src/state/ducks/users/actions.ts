import { Types } from "./types";
import { CALL_API } from "../../middlewares/apiService";

function fetchUser(id: string) {
  return {
    [CALL_API]: {
      endpoint: `/api/users/${id}`,
      types: [Types.USER_REQUEST, Types.USER_SUCCESS, Types.USER_FAILURE],
    },
  };
}

export function loadUser(id: string) {
  return function (dispatch: any, getState: any) {
    const user = getState().users.entities.get(id);
    // do not send pointless requests
    if (user || !id) {
      return null;
    }
    return dispatch(fetchUser(id));
  };
}

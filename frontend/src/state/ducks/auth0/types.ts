export enum Types {
  INIT_AUTH0_REQUEST = "INIT_AUTH0_REQUEST",
  INIT_AUTH0_SUCCESS = "INIT_AUTH0_SUCCESS",
  RECEIVE_LOGIN = 'RECEIVE_LOGIN'
}

interface requestInitAuth0Action {
  type: typeof Types.INIT_AUTH0_REQUEST;
}

interface successAuth0Action {
  type: typeof Types.INIT_AUTH0_SUCCESS;
  payload: any;
}

interface receiveLoginAction {
  type: typeof Types.RECEIVE_LOGIN,
  payload: any
}

export type Auth0ActionTypes =
  | requestInitAuth0Action
  | successAuth0Action
  | receiveLoginAction;

export default Types;

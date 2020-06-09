export enum Types {
  INIT_AUTH0_REQUEST = "INIT_AUTH0_REQUEST",
  INIT_AUTH0_SUCCESS = "INIT_AUTH0_SUCCESS",
  RECIEVE_LOGIN = 'RECIEVE_LOGIN'
}

interface requestInitAuth0Action {
  type: typeof Types.INIT_AUTH0_REQUEST;
}

interface successAuth0Action {
  type: typeof Types.INIT_AUTH0_SUCCESS;
  payload: any;
}

interface recieveLoginAction {
  type: typeof Types.RECIEVE_LOGIN,
  payload: any
}

export type Auth0ActionTypes =
  | requestInitAuth0Action
  | successAuth0Action
  | recieveLoginAction;

export default Types;

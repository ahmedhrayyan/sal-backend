export enum Types {
  INIT_AUTH0_REQUEST = "INIT_AUTH0_REQUEST",
  INIT_AUTH0_SUCCESS = "INIT_AUTH0_SUCCESS",
  INIT_AUTH0_ERROR = 'INIT_AUTH0_ERROR'
}

interface requestInitAuth0Action {
  type: typeof Types.INIT_AUTH0_REQUEST;
}

interface successAuth0Action {
  type: typeof Types.INIT_AUTH0_SUCCESS;
  payload: any;
}

interface initAuth0ErrorAction {
  type: typeof Types.INIT_AUTH0_ERROR,
  error: string
}

export type Auth0ActionTypes =
  | requestInitAuth0Action
  | successAuth0Action
  | initAuth0ErrorAction;

export default Types;

import Types, { Auth0ActionTypes } from './types';
const defaultState = {
  isAuthenticated: false,
  isLoading: false,
  user: null,
  auth0Client: null
}

function auth0Reducer(state = defaultState, action: Auth0ActionTypes) {
  switch (action.type) {
    case Types.INIT_AUTH0_REQUEST:
      return Object.assign({}, state, {
        isLoading: true,
      })
    case Types.INIT_AUTH0_SUCCESS:
      return Object.assign({}, state, {
        isLoading: false,
        auth0Client: action.payload
      })
    case Types.RECIEVE_LOGIN:
      return Object.assign({}, state, {
        isAuthenticated: true,
        user: action.payload
      })
    default:
      return state;
  }
}

export default auth0Reducer;

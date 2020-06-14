import Types, { Auth0ActionTypes } from './types';
import createAuth0Client, { Auth0Client } from "@auth0/auth0-spa-js";

function requestInitAuth0(): Auth0ActionTypes {
  return {
    type: Types.INIT_AUTH0_REQUEST
  }
}

function initAuth0Success(auth0Client: Auth0Client): Auth0ActionTypes {
  return {
    type: Types.INIT_AUTH0_SUCCESS,
    payload: auth0Client
  }
}

function initAuth0Error(error: string): Auth0ActionTypes {
  return {
    type: Types.INIT_AUTH0_ERROR,
    error
  }
}

// async action

interface InitOptions {
  domain: string,
  client_id: string,
  audience: string,
  redirect_uri: string,
  useRefreshToken: boolean
}
function defaultHandleRedirect(appState?: any) {
  window.history.replaceState({}, document.title, window.location.pathname);
}

export function initAuth0(initOptions: InitOptions, handleRedirect = defaultHandleRedirect) {
  return function(dispatch: any) {
    dispatch(requestInitAuth0())
    createAuth0Client(initOptions)
      .then((auth0Client: Auth0Client) => {
        // handle authentication from the url
        if (
          window.location.search.includes('code=') &&
          window.location.search.includes('state=')
        ) {
          auth0Client.handleRedirectCallback().then(appState => handleRedirect(appState))
        }
        return auth0Client
      })
      .then(auth0Client => {
        dispatch(initAuth0Success(auth0Client))
      })
      .catch(err => {
        dispatch(initAuth0Error(err.message))
      });
  }
}

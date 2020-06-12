import Types, { Auth0ActionTypes } from './types';
import createAuth0Client from "@auth0/auth0-spa-js";

function requestInitAuth0(): Auth0ActionTypes {
  return {
    type: Types.INIT_AUTH0_REQUEST
  }
}

function initAuth0Success(auth0Client: any): Auth0ActionTypes {
  return {
    type: Types.INIT_AUTH0_SUCCESS,
    payload: auth0Client
  }
}

function receiveLogin(user: any): Auth0ActionTypes {
  return {
    type: Types.RECEIVE_LOGIN,
    payload: user
  }
}

// async action

interface InitOptions {
  domain: string,
  client_id: string,
  redirect_uri: string
}
function defaultHandleRedirect(appState?: any) {
  window.history.replaceState({}, document.title, window.location.pathname);
}

export function initAuth0(initOptions: InitOptions, handleRedirect = defaultHandleRedirect) {
  return async function(dispatch: any) {
    dispatch(requestInitAuth0())
    const auth0Client = await createAuth0Client(initOptions);

    // handle authentication from the url
    if (
      window.location.search.includes('code=') &&
      window.location.search.includes('state=')
    ) {
      const { appState } = await auth0Client.handleRedirectCallback();
      handleRedirect(appState)
    }
    const isAuthenticated = await auth0Client.isAuthenticated();
    if (isAuthenticated) {
      const user = await auth0Client.getUser();
      dispatch(receiveLogin(user))
    }

    dispatch(initAuth0Success(auth0Client))
  }
}

import Types, { Auth0ActionTypes, SuccessPayload } from "./types";
import createAuth0Client, { Auth0Client } from "@auth0/auth0-spa-js";

function requestInitAuth0(): Auth0ActionTypes {
  return {
    type: Types.INIT_AUTH0_REQUEST,
  };
}

function initAuth0Success(successPayload: SuccessPayload): Auth0ActionTypes {
  return {
    type: Types.INIT_AUTH0_SUCCESS,
    payload: successPayload,
  };
}

function initAuth0Error(error: string): Auth0ActionTypes {
  return {
    type: Types.INIT_AUTH0_ERROR,
    error,
  };
}

// async action

interface InitOptions {
  domain: string;
  client_id: string;
  audience: string;
  redirect_uri: string;
  useRefreshToken: boolean;
}
function defaultHandleRedirect(appState?: any) {
  window.history.replaceState({}, document.title, window.location.pathname);
}

export function initAuth0(
  initOptions: InitOptions,
  handleRedirect = defaultHandleRedirect
) {
  return function (dispatch: any) {
    dispatch(requestInitAuth0());
    createAuth0Client(initOptions)
      .then(async (auth0Client) => {
        // handle authentication from the url
        if (
          window.location.search.includes("code=") &&
          window.location.search.includes("state=")
        ) {
          const appState = await auth0Client.handleRedirectCallback();
          handleRedirect(appState);
        }
        const isAuthenticated = await auth0Client.isAuthenticated();
        let accessToken = null,
          currentUser = null;
        if (isAuthenticated) {
          accessToken = await auth0Client.getTokenSilently();
          // get current user id from json web token
          currentUser = JSON.parse(atob(accessToken.split(".")[1])).sub;
        }
        dispatch(
          initAuth0Success({
            auth0Client,
            isAuthenticated,
            accessToken,
            currentUser,
          })
        );
      })
      .catch((err) => {
        dispatch(initAuth0Error(err.message));
      });
  };
}

import React, { useEffect } from "react";
import config from "../../auth_config.json";
import history from "../../state/ducks/auth0/utils";
import { initAuth0 } from "../../state/ducks/auth0/actions";
import { loadUser } from "../../state/ducks/users/actions";
import { connect } from "react-redux";
import { Router, Route } from "react-router-dom";
import routes from "../../routes";
import { Header, Spinner } from "../components";

interface Props {
  initAuth0: any,
  isLoading: boolean,
  isAuthenticated: boolean,
  token: string;
  currentUser: string;
  loadUser: any;
}
function App(props: Props) {
  useEffect(() => {
    const handleAuth0Redirect = (appState: any) => {
      history.push(
        appState && appState.targetUrl
          ? appState.targetUrl
          : window.location.pathname
      );
    };

    props.initAuth0(
      {
        domain: config.domain,
        client_id: config.clientId,
        audience: config.audience,
        redirect_uri: window.location.origin,
        useRefreshToken: config.useRefreshToken
      },
      handleAuth0Redirect
    );
  }, []);
  useEffect(() => {
    // load currentUser
    if (props.isAuthenticated) {
      props.loadUser(props.token, props.currentUser)
    }
  }, [props.isAuthenticated])

  if (props.isLoading) {
    return (
      <div className="app">
        <Spinner className="spinner spinner-centered"/>
      </div>
    )
  }

  return (
    <Router history={history}>
      <Header />
      {props.isAuthenticated && <div>
        {routes.map(route => {
          return (
            <Route key={route.path} {...route} />
          )
        })}
      </div>}
    </Router>
  )
}

function mapStateToProps(state: any) {
  return {
    isLoading: state.auth0.isLoading,
    isAuthenticated: state.auth0.isAuthenticated,
    currentUser: state.auth0.currentUser,
    token: state.auth0.accessToken
  }
}

const mapDispatchToProps = {
  initAuth0,
  loadUser
}

export default connect(mapStateToProps, mapDispatchToProps)(App);

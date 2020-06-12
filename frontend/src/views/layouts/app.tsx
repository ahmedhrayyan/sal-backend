import React, { useEffect } from "react";
import config from "../../auth_config.json";
import history from "../../state/ducks/auth0/utils";
import { initAuth0 } from "../../state/ducks/auth0/actions";
import { connect } from "react-redux";
import { Router, Route } from "react-router-dom";
import routes from "../../routes";
import { Header, Spinner } from "../components";

interface Props {
  isLoading: boolean,
  initAuth0: any
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
      },
      handleAuth0Redirect
    );
  }, []);

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
      <div className="app">
        {routes.map(route => {
          return (
            <Route key={route.path} {...route} />
          )
        })}
      </div>
    </Router>
  )
}

function mapStateToProps(state: any) {
  return {
    isLoading: state.auth0.isLoading
  }
}

const mapDispatchToProps = {
  initAuth0
}

export default connect(mapStateToProps, mapDispatchToProps)(App);

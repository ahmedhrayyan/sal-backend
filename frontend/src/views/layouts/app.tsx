import React, { useEffect } from "react";
import config from "../../auth_config.json";
import history from "../../state/ducks/auth0/utils";
import { initAuth0 } from "../../state/ducks/auth0/actions";
import { connect } from "react-redux";

interface Props {
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
        redirect_uri: window.location.origin,
      },
      handleAuth0Redirect
    );
  }, []);

  return <div className="App"></div>;
}

const mapStateToProps = {
  initAuth0
}

export default connect(null, mapStateToProps)(App);

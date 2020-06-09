import React from "react";
import ReactDOM from "react-dom";
import "./style/main.scss";
import { App } from "./views/layouts";
import * as serviceWorker from "./serviceWorker";
import { Provider as ReduxProvider } from "react-redux";
import store from "./state/store";


ReactDOM.render(
  <React.StrictMode>
    <ReduxProvider store={store}>
      <App />
    </ReduxProvider>
  </React.StrictMode>,
  document.getElementById("root")
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();

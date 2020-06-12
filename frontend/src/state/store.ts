import thunkMiddleware from "redux-thunk";
import { createLogger } from "redux-logger";
import { createStore, applyMiddleware } from "redux";
import { auth0 } from "./ducks";
import apiService from "./middlewares/apiService";

const loggerMiddleware = createLogger();

const store = createStore(
  auth0,
  applyMiddleware(
    apiService,
    thunkMiddleware,
    loggerMiddleware
  )
);

export default store;

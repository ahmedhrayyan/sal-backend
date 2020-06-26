import thunkMiddleware from "redux-thunk";
// import { createLogger } from "redux-logger";
import { createStore, applyMiddleware, combineReducers } from "redux";
import * as reducers from "./ducks";
import apiService from "./middlewares/apiService";

// const loggerMiddleware = createLogger();

const store = createStore(
  combineReducers(reducers),
  applyMiddleware(
    apiService,
    thunkMiddleware
    // loggerMiddleware
  )
);

export default store;

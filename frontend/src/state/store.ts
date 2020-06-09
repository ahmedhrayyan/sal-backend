import thunkMiddleware from "redux-thunk";
import { createLogger } from "redux-logger";
import { createStore, applyMiddleware } from "redux";
import { auth0 } from "./ducks";

const loggerMiddleware = createLogger();

const store = createStore(
  auth0,
  applyMiddleware(thunkMiddleware, loggerMiddleware)
);

export type Store = typeof store;
export default store;

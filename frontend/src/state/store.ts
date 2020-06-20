import thunkMiddleware from "redux-thunk";
import { createStore, applyMiddleware, combineReducers } from "redux";
import * as reducers from "./ducks";
import apiService from "./middlewares/apiService";

const store = createStore(
  combineReducers(reducers),
  applyMiddleware(apiService, thunkMiddleware)
);

export default store;

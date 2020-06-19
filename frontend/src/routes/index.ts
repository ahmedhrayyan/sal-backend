import React from "react";
import { Home } from "../views/pages";
import { QuestionPage } from "../views/pages";
import { RouteProps } from "react-router-dom";
const routes = [
  {
    path: "/",
    component: Home,
    exact: true,
  },
  {
    path: "/questions/:questionId",
    component: QuestionPage,
    exact: true
  }
];

export default routes;

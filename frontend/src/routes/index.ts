import { Home } from "../views/pages";
import { QuestionPage } from "../views/pages";
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

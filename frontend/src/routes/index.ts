import { Home } from "../views/pages";
import { QuestionPage } from "../views/pages";
import { SearchPage } from "../views/pages";
const routes = [
  {
    path: "/",
    component: Home,
    exact: true,
  },
  {
    path: "/questions/:questionId",
    component: QuestionPage,
    exact: true,
  },
  {
    path: "/search",
    component: SearchPage,
    exact: true
  }
];

export default routes;

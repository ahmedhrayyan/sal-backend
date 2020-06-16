export enum Types {
  QUESTIONS_REQUEST = "QUESTIONS_REQUEST",
  QUESTIONS_SUCCESS = "QUESTIONS_SUCCESS",
  QUESTIONS_FAILURE = "QUESTIONS_FAILURE",
  Q_DELETE_REQUEST = "Q_DELETE_REQUEST",
  Q_DELETE_SUCCESS = "Q_DELETE_SUCCESS",
  Q_DELETE_FAILURE = "Q_DELETE_FAILURE",
  Q_POST_REQUEST = 'Q_POST_REQUEST',
  Q_POST_SUCCESS = 'Q_POST_SUCCESS',
  Q_POST_FAILURE = 'Q_POST_FAILURE',
  Q_BA_REQUEST = 'Q_BA_REQUEST', // question best answer
  Q_BA_SUCCESS = 'Q_BA_SUCCESS',
  Q_BA_FAILURE = 'Q_BA_FAILURE'
}

export interface Question {
  id: number;
  user_id: string;
  content: string;
  created_at: string;
  best_answer: number;
  latest_answer: number;
  no_of_answers: number;
};

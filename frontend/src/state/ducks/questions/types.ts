export enum Types {
  QUESTIONS_REQUEST = "QUESTIONS_REQUEST",
  QUESTIONS_SUCCESS = "QUESTIONS_SUCCESS",
  QUESTIONS_FAILURE = 'QUESTIONS_FAILURE',
  Q_DELETE_REQUEST = 'Q_DELETE_REQUEST',
  Q_DELETE_SUCCESS = 'Q_DELETE_SUCCESS',
  Q_DELETE_FAILURE = 'Q_DELETE_FAILURE'
}

export type Question = {
  id: number;
  user_id: string;
  content: string;
  created_at: string;
  best_answer_id: number;
  no_of_answers: number;
}

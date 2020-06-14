export enum Types {
  ANSWER_REQUEST = "ANSWER_REQUEST",
  ANSWER_SUCCESS = "ANSWER_SUCCESS",
  ANSWER_FAILURE = "ANSWER_FAILURE",
  A_DELETE_REQUEST = "A_DELETE_REQUEST",
  A_DELETE_SUCCESS = "A_DELETE_SUCCESS",
  A_DELETE_FAILURE = "A_DELETE_FAILURE",
}

export interface Answer {
  id: number;
  user_id: string;
  content: string;
  created_at: string;
  question_id: number;
};

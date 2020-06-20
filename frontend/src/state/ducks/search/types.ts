export enum Types {
  SEARCH_REQUEST = "SEARCH_REQUEST",
  SEARCH_SUCCESS = "SEARCH_SUCCESS",
  SEARCH_FAILURE = "SEARCH_FAILURE",
}

export interface Question {
  id: number;
  user_id: string;
  content: string;
  created_at: string;
  best_answer: number | null;
  answers: number[];
}

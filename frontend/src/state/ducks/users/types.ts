export enum Types {
  USER_REQUEST = "USER_REQUEST",
  USER_SUCCESS = "USER_SUCCESS",
  USER_FAILURE = 'USER_FAILURE',
}

export interface User {
  name: string; // given name by auth0
  picture: string;
  user_metadata?: {
    firstname: string;
    lastname: string;
    job: string;
  }
}

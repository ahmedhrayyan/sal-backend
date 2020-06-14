const baseUrl = "";

function callApi(endpoint: string, token?: string, method?: string) {
  let config: any = {};
  if (token) {
    config = {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    };
  }
  if (method) {
    Object.assign(config, {
      method
    })
  }

  return fetch(baseUrl + endpoint, config)
    .then((response) => {
      return response.json().then((data) => ({ data, response }));
    })
    .then(({ data, response }) => {
      if (!response.ok) {
        return Promise.reject(data);
      }

      return data;
    });
}

export const CALL_API = Symbol("Call API");
const apiService = () => (next: any) => (action: any) => {
  const call = action[CALL_API];

  // So the middleware doesn't get applied to every single action
  if (typeof call === "undefined") {
    return next(action);
  }

  let { endpoint, token, types, method='GET' } = call;
  const [ requestType, successType, errorType ] = types
  // dispatching the request
  next({
    type: requestType
  })

  return callApi(endpoint, token, method)
  .then(response => {
    return next({
      receivedAt: Date.now(),
      payload: response,
      type: successType
    })
  })
  .catch(error => {
    return next({
      error: error.message,
      type: errorType
    })
  })
};

export default apiService

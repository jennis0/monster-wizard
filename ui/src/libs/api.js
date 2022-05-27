/**
 * Wrap a promise API with a function that will attempt the promise over and over again
 * with exponential backoff until it resolves or reaches the maximum number of retries.
 *   - First retry: 500 ms + <random> ms
 *   - Second retry: 1000 ms + <random> ms
 *   - Third retry: 2000 ms + <random> ms
 * and so forth until maximum retries are met, or the promise resolves.
 */
const ADDRESS = "http://127.0.0.1:8000"

 const withRetries = ({ attempt, maxRetries, onUpdateCallback=null }) => async (...args) => {
    const slotTime = 250;
    let retryCount = 0;
    do {
      try {
        console.log('Attempting...', Date.now(), onUpdateCallback);
        const result = await attempt(...args).then(r => r.json());
        if (onUpdateCallback) {
          onUpdateCallback(result)
        }
        console.log("result", result);
        if (result.state === "error") {
            return Promise.reject(result)
        }
        if (result.state === "finished") {
            return Promise.resolve(result)
        }
      } catch (error) {
        const isLastAttempt = retryCount === maxRetries;
        if (isLastAttempt) {
          // Stack Overflow console doesn't show unhandled
          // promise rejections so lets log the error.
          console.error("error", error);
          return Promise.reject(error);
        }
      }
      const delay = 2 ** Math.min(retryCount, 5) * slotTime
      // Wait for the exponentially increasing delay period before retrying again.
      await new Promise(resolve => setTimeout(resolve, delay));
    } while (retryCount++ < maxRetries);
  }


export function post_file(data, onSuccessCallback, onErrorCallback=null, onUpdateCallback=null) {

    const getResult = (id) => fetch(`${ADDRESS}/process/?id=${id}`, {method:"GET"})
    const getResultWithRetries = withRetries( {attempt:getResult, maxRetries:100, onUpdateCallback:onUpdateCallback} )

    fetch(`${ADDRESS}/process/`,
    {
        method:"POST", body: data
    })
    .then(r => r.json(), (e) => {console.log("error", e)})
    .then(r =>  {
        if (r.state !== "error") {
            getResultWithRetries(r.id).then(onSuccessCallback, onErrorCallback)
        } else {
            if(onErrorCallback) {
                onErrorCallback(r)
            }
        }
    }, () => {})
};

export function reparse_feature(title, text, onSuccessCallback, onErrorCallback=null) {
  fetch(`${ADDRESS}/parse/`,
  {
    method:"POST", 
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({title:title, text:text, type:"feature"})
  })
    .then(r => r.json(), (e) => {console.log("error", e)})
    .then(r => {
      if (r.error) {
        onErrorCallback(r)
      } else {
        onSuccessCallback(r)
      }
    })
}

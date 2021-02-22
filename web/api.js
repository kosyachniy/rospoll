import axios from 'axios';


function serverRequest(json={}, token='') {
    const headers = { headers: {}}
    if (token) {
    	headers.headers.Authorization = `Bearer ${token}`;
    }
    return axios.post('https://rospoll.online/api/', json, headers)
}

function handlerResult(that, res, handlerSuccess, handlerError) {
    if (res.error) {
        // console.log(res)
        handlerError(that, res)
    } else {
        // console.log(res)
        handlerSuccess(that, res)
    }
}

export default function api(that, method, params = {}, token='', handlerSuccess = () => {},
    handlerError = () => {}) {
    const json = {
        method,
        params,
    }

    // console.log(json, token)

    serverRequest(json, token).then((res) => handlerResult(that, res.data, handlerSuccess, handlerError))
}

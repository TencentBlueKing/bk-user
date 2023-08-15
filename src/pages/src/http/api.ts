import fetch from './fetch';

const apiPerfix = '/api/v1/web';

export const getUser = () => fetch.get(`${apiPerfix}/user`);

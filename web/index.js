import { useState, useEffect } from 'react';
import bridge from '@vkontakte/vk-bridge';

import api from './api';


const App = () => {
	const [user, setUser] = useState(null);
	const [token, setToken] = useState("");

	useEffect(() => {
		bridge.send('VKWebAppInit');

		async function fetchData() {
			const url = document.location.search;

			api(this, 'account.auth', { url }, '', (_, e) => {
				setUser(e.result);
				if (e.result && e.result.token) {
					setToken(e.result.token);
				}
			})
		}

		fetchData();
	}, []);
}


export default App;
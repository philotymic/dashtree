import React from 'react';
import ReactDOM from 'react-dom';
import {connectToServer} from 'libdipole-js';
import App from './App.js';

connectToServer("ws://localhost:3456").then((ws_handler) => {
    ReactDOM.render(<App ws_handler={ws_handler}/>,
		    document.getElementById('root'));
});

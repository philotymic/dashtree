import React from 'react';

import './gen-js/all-mods.js';
let Topics = window.Topics;

class TopicSubscriberI extends Topics.TopicSubscriber {
    constructor (app_obj) {
	super();
	this.app_obj = app_obj;
    }
    
    onTopicStateChange(topic_path, topic_state) {
	console.log("TopicSubscriberI::onTopicStateChange:", topic_path, topic_state);
	//const rows = topic_messages;
	//this.app_obj.setState({columns: this.columns, tableColumnExtensions: this.tableColumnExtensions, rows: rows});
    }
};

function getBackendProxyString()
{
    return new Promise((resolve, reject) => {
	// this function is defined in python
	getBackendPort("hello from js", (port) => {
	    if (port) {
		let proxy_s = `topics:ws -h localhost -p ${port}`;
		resolve(proxy_s);
	    } else {
		reject("getBackendPort returns null/undef");
	    }
	});
    });
}

class App extends React.Component {
    constructor (props) {
	super(props);
	this.columns = [ {name: 'topic', title: 'Topic'},
			 {name: 'message', title: 'Message'},
			 {name: 'status', title: 'Status'}];
	this.tableColumnExtensions = [{ columnName: 'topic', width: 300 }];
	this.state = {
	    columns: this.columns,
	    tableColumnExtensions: this.tableColumnExtensions,
	    rows: []
	}
    }
    
    componentDidMount() {
	let backend_proxy_s = null;
	getBackendProxyString().then((backend_proxy_s_) => {
	    backend_proxy_s = backend_proxy_s_;
	    return window.ic.createObjectAdapter("");
	}).then((adapter) => {
	    this.adapter = adapter;
	    console.log("backend_proxy_s:", backend_proxy_s);
	    let o_prx = window.ic.stringToProxy(backend_proxy_s); //"topics:ws -h localhost -p 12345");
	    return Topics.TopicsSubscriptionsPrx.checkedCast(o_prx);
	}).then((prx) => {
	    this.center_proxy = prx;
	    this.connection = this.center_proxy.ice_getCachedConnection();
	    this.connection.setAdapter(this.adapter);
	}).then(() => {
	    let subscriber_o_prx = this.adapter.addWithUUID(new TopicSubscriberI(this));
	    return this.center_proxy.subscribeViaIdentity(subscriber_o_prx.ice_getIdentity());
	}).then(() => {
	    console.log("subscription is all set");
	});
    }

    render () {
	return (<h1>Hello</h1>);
    }
};

export default App;

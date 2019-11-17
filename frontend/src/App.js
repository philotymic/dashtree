import React from 'react';
import Paper from '@material-ui/core/Paper';
import {
  TreeDataState,
  CustomTreeData,
} from '@devexpress/dx-react-grid';
import {
  Grid,
  Table,
  TableHeaderRow,
  TableTreeColumn,
} from '@devexpress/dx-react-grid-material-ui';

let Topics = window.Topics;

class TopicSubscriberI extends Topics.TopicSubscriber {
    constructor (app_obj) {
	super();
	this.app_obj = app_obj;
    }
    
    onTopicStateChange(topic_path, topic_state) {
	console.log("TopicSubscriberI::onTopicStateChange:", topic_path, topic_state);
	this.app_obj.update_row(topic_path, topic_state);
    }
};

//
// ll is subpath of rr. I.e ll is parent of rr
//
// NOTE right implementation should give /a /a/c/cc give false, /a /a/c should give true
//
function subpath_of(ll, rr) {
    var ret = null;
    if (ll) {
	//console.log("ll rr rr-1:", ll, rr, rr.split("/").splice(-1,1).join("/"));
	let rrm1 = rr.split("/"); rrm1.pop();
	ret = ll.split("/").join("/") === rrm1.join("/");
    } else {
	ret = rr.split("/").length === 2;
    }
    //console.log("subpath_of:", ll, rr, ret);
    return ret;
}


const getChildRows = (row, rootRows) => {
    const row_topic = row ? row.topic : null;
    const childRows = rootRows.filter(r => subpath_of(row_topic, r.topic))
    let ret = childRows.length ? childRows : null;
    return ret;
};


class App extends React.PureComponent {
    constructor (props) {
	super(props);
	this.columns = [{name: 'topic', title: 'Topic'},
			{name: 'message', title: 'Message'},
			{name: 'status', title: 'Status'}];
	this.tableColumnExtensions = [{columnName: 'topic', width: 300}];
	this.state = {
	    columns: this.columns,
	    tableColumnExtensions: this.tableColumnExtensions,
	    rows_d: {},
	    rows: []
	}
    }
    
    componentDidMount() {
	let backend_proxy_s = null;
	getBackendPort().then((backend_port) => {
	    backend_proxy_s = `topics:ws -h localhost -p ${backend_port}`;
	    return window.ic.createObjectAdapter("");
	}).then((adapter) => {
	    this.adapter = adapter;
	    console.log("backend_proxy_s:", backend_proxy_s);
	    let o_prx = window.ic.stringToProxy(backend_proxy_s);
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

    update_row(row_key, row_value) {
	let new_rows_d = Object.assign(this.state.rows_d,
				       {[row_key]: {topic: row_key, message: row_value, status: 'OKKK'}});
	let new_state = {...this.state,
			 rows_d: new_rows_d,
			 rows: Object.values(new_rows_d)
			};
			
	this.setState(new_state);
    }
    
    render () {
	return (
		<Paper>
		<Grid
            rows={this.state.rows}
            columns={this.state.columns}
		>
		<TreeDataState />
		<CustomTreeData
            getChildRows={getChildRows}
		/>
		<Table
            columnExtensions={this.state.tableColumnExtensions}
		/>
		<TableHeaderRow />
		<TableTreeColumn
            for="topic"
		/>
		</Grid>
		</Paper>
	);
    }
};

export default App;

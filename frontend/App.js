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
import * as backend from './gen-js/backend.js';

function generateQuickGuid() {
    return Math.random().toString(36).substring(2, 15) +
        Math.random().toString(36).substring(2, 15);
}


class TopicSubscriberI extends backend.TopicSubscriber {
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
	let center_prx = new backend.TopicsSubscriptionsPrx(this.props.ws_handler, "topics");
	let subscriber_o = new TopicSubscriberI(this);
	let o_id = generateQuickGuid();
	this.props.ws_handler.object_server.add_object(o_id, subscriber_o);
	center_prx.subscribe(o_id).then(() => console.log("subscription is all set"));
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

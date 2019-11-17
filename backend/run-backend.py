# python run-backend.py               -- publish/subscriber server
# python run-tests.py test-publish    -- publisher
# python run-tests.py test-subscriber -- subscriber
#
import Ice, sys, os
import prctl, signal

if not 'topdir' in os.environ:
    raise Exception("no topdir specified in env")

Ice.loadSlice("--all -I{ICE_SLICE_DIR} {top}/backend/backend.ice".format(ICE_SLICE_DIR = Ice.getSliceDir(), top = os.environ['topdir']))
import Topics

class TopicSubscriptionsI(Topics.TopicsSubscriptions):
    def __init__(self):
        self.topics = {} # topic -> text
        self.subscribers = [] # proxies to TopicSubsriber objects
        
    def getTopicPathes(self, curr = None):
        return self.topics.keys()

    def getTopicState(self, topic_path, curr = None):
        return self.topics[topic_path] if topic_path in self.topics else None

    def publish(self, topic_path, topic_state, curr = None):
        print "TopicSubscriptionsI::publish:", topic_path, topic_state, len(self.subscribers)
        self.topics[topic_path] = topic_state
        for subscriber in self.subscribers[:]:
            try:
                subscriber.onTopicStateChange(topic_path, topic_state)
            except Ice.Exception as ex:
                print "ice exception:", ex
                self.subscribers.remove(subscriber)
                print "len of subscriber:", len(self.subscribers)

    def subscribeViaProxy(self, subscriber_prx, curr = None):
        print "TopicsSubscriptionsI::subscribeViaProxy:", subscriber_prx
        self.subscribers.append(subscriber_prx)

    def subscribeViaIdentity(self, subscriber_id, curr = None):
        print "TopicsSubscriptionsI::subscribeViaIdentity:", subscriber_id
        #subscriber_ice_identity = Ice.Identity(name = subscriber_id)
        bidir_prx = Topics.TopicSubscriberPrx.uncheckedCast(curr.con.createProxy(subscriber_id))
        self.subscribers.append(bidir_prx)
        
if __name__ == "__main__":
    # https://github.com/seveas/python-prctl -- prctl wrapper module
    # more on pdeathsignal: https://stackoverflow.com/questions/284325/how-to-make-child-process-die-after-parent-exits
    prctl.set_pdeathsig(signal.SIGTERM) # if parent dies this child will get SIGTERM
    
    props = Ice.createProperties()
    props.setProperty("Ice.ThreadPool.Server.Size", "2")
    props.setProperty("Ice.ACM.Close", "0")
    props.setProperty("Ice.MessageSizeMax", "0")
    #props.setProperty("Ice.Trace.Protocol", "1")
    #props.setProperty("Ice.Trace.Network", "3")

    init_data = Ice.InitializationData()
    init_data.properties = props

    with Ice.initialize(sys.argv, init_data) as communicator:
        xfn_fn = sys.argv[1]
        # server
        port = 0
        adapter = communicator.createObjectAdapterWithEndpoints("", "ws -p {port}".format(port = port))
        endpoints = adapter.getEndpoints()
        ep_s = endpoints[0].toString()
        print ep_s
        port = int(ep_s.split(" ")[2])
        print "running server at port", port
        xfn_fd = open(xfn_fn, "w+b")
        print >>xfn_fd, port
        xfn_fd.close()
        print "port assigned"
        sys.stdout.flush()

        adapter.add(TopicSubscriptionsI(), Ice.stringToIdentity("topics"))
        adapter.activate()
        communicator.waitForShutdown()
        
        


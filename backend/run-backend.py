# python run-backend.py               -- publish/subscriber server
# python run-tests.py test-publish    -- publisher
# python run-tests.py test-subscriber -- subscriber
#
#import ipdb
import sys, os, asyncio
import prctl, signal

import websockets
sys.path.append(os.path.join(os.environ['dipole_topdir'], "src"))
import libdipole
import libdipole.autoport

@libdipole.interface
class TopicSubscriptions:
    def getTopicPathes(self): pass
    def getTopicState(self, topic_path): pass
    def publish(self, topic_path, topic_state): pass
    def subscribe(self, subscriber_id): pass
    
class TopicSubscriptions(TopicSubscriptions)
    def __init__(self):
        self.topics = {} # topic -> text
        self.subscribers = [] # proxies to TopicSubsriber objects
        
    def getTopicPathes(self):
        return self.topics.keys()

    def getTopicState(self, topic_path):
        return self.topics[topic_path] if topic_path in self.topics else None

    def publish(self, topic_path, topic_state):
        print("TopicSubscriptionsI::publish:", topic_path, topic_state, len(self.subscribers))
        self.topics[topic_path] = topic_state
        for subscriber in self.subscribers[:]:
            subscriber.onTopicStateChange(topic_path, topic_state)

    def subscribe(self, subscriber_id):
        print("TopicsSubscriptionsI::subscribe:", subscriber_id)
        self.subscribers.append(subscriber_id)
        
if __name__ == "__main__":
    # https://github.com/seveas/python-prctl -- prctl wrapper module
    # more on pdeathsignal: https://stackoverflow.com/questions/284325/how-to-make-child-process-die-after-parent-exits
    prctl.set_pdeathsig(signal.SIGTERM) # if parent dies this child will get SIGTERM
    
    xfn_fn = sys.argv[1]

    ws_handler = libdipole.WSHandler();
    print("adding object topic_subscriptions")
    ws_handler.object_server.add_object("topics", TopicSubscriptions())

    ws_l = websockets.serve(ws_handler.message_loop, 'localhost', 0)
    asyncio.get_event_loop().run_until_complete(ws_l)
    assigned_port = libdipole.autoport.find_ws_port(ws_l)
    libdipole.__save_assigned_port(assigned_port, xfn)
    asyncio.get_event_loop().run_forever()

        


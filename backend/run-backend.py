# python run-backend.py               -- publish/subscriber server
# python run-tests.py test-publish    -- publisher
# python run-tests.py test-subscriber -- subscriber
#
#import ipdb
import sys, os, asyncio, asgiref.sync
import prctl, signal

import websockets
sys.path.append("/home/asmirnov/dipole/src")
import libdipole
sys.path.append("gen-py")
import backend

class TopicsSubscriptionsI(backend.TopicsSubscriptions):
    def __init__(self):
        self.topics = {} # topic -> text
        self.subscribers = [] # proxies to TopicSubsriber objects
        
    async def getTopicPathes(self):
        return list(self.topics.keys())

    async def getTopicState(self, topic_path):
        return self.topics[topic_path] if topic_path in self.topics else None

    async def publish(self, topic_path, topic_state):
        print("TopicSubscriptionsI::publish:", topic_path, topic_state, len(self.subscribers))
        self.topics[topic_path] = topic_state
        for subscriber in self.subscribers[:]:
            await subscriber.onTopicStateChange(topic_path, topic_state)

    async def subscribe(self, subscriber_obj_id, ctx):
        print("TopicsSubscriptionsI::subscribe:", subscriber_obj_id)
        subscriber_prx = backend.TopicSubscriberPrx(ctx.ws_handler, subscriber_obj_id)
        self.subscribers.append(subscriber_prx)
        
if __name__ == "__main__":
    object_server = libdipole.ObjectServer()
    ws_handler_f = libdipole.WSHandlerFactory(object_server)
    print("adding object topics")
    object_server.add_object("topics", TopicsSubscriptionsI())

    ws_l = websockets.serve(ws_handler_f.server_message_loop, 'localhost', 3456)
    asyncio.get_event_loop().run_until_complete(ws_l)
    asyncio.get_event_loop().run_forever()

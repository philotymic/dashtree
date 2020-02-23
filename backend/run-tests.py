import sys, time
import asyncio, uuid
sys.path.append("/home/asmirnov/dipole/src")
import libdipole
sys.path.append("gen-py")
import backend

class TopicSubscriberI(backend.TopicSubscriber):
    async def onTopicStateChange(self, topic_path, topic_state):
        print("TopicSubscriberI::onTopicStateChange:", topic_path, topic_state)

async def publisher(ws_handler):
    print("round-robin test publisher")
    test_topics = ["/a", "/a/b", "/b", "/b/d"]
    test_topic_states = ["NONE|", "OK|ok", "ERR|system failure"]
    center_prx = backend.TopicsSubscriptionsPrx(ws_handler, "topics")
    while 1:
        for test_topic in test_topics:
            for test_topic_state in test_topic_states:
                print("publish:", test_topics, test_topic_states)
                await center_prx.publish(test_topic, test_topic_state)
                await asyncio.sleep(5)

async def subscriber(ws_handler):
    print("entering subscriber")
    center_prx = backend.TopicsSubscriptionsPrx(ws_handler, "topics")
    if 0:
        print("topics:", await center_prx.getTopicPathes())
        print("topic states:")
        for topic in await center_prx.getTopicPathes():
            print(topic, "-->", await center_prx.getTopicState(topic))

    obj = TopicSubscriberI()
    obj_id = str(uuid.uuid1())
    ws_handler.object_server.add_object(obj_id, obj)
    await center_prx.subscribe(obj_id)
    print("start listening")
    await asyncio.sleep(1000000)
    
async def main():
    test_type = sys.argv[1]
    port = int(sys.argv[2])
    object_server = libdipole.ObjectServer()
    ws_handler = libdipole.WSHandler(object_server);
    ws_url = f"ws://localhost:{port}"
    await ws_handler.client_message_loop(ws_url)
    
    if test_type == "test-publisher":
        await asyncio.create_task(publisher(ws_handler))
    elif test_type == "test-subscriber":
        await asyncio.create_task(subscriber(ws_handler))
    else:
        print("exception")
        raise Exception("unknown test_type %s" % test_type)

if __name__ == "__main__":
    res = asyncio.run(main())    
    print("__main__: all done", res)
    
    

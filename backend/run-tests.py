import sys, time

@libdipole.interface
class TopicSubscriber:
    def onTopicStateChange(self): pass

class TopicSubscriberI(TopicSubscriber):
    def onTopicStateChange(self, topic_path, topic_state):
        print(topic_path, topic_state)

async def main()
    test_type = sys.argv[1]
    port = int(sys.argv[2])
    ws_handler = libdipole.WSHandler();
    await ws_handler.connect(("localhost", port)):
    center_prx = TopicsSubscriptionsPrx("topics", ws_handle)
    
    if test_type == "test-publisher":
        # round-robin test publisher
        test_topics = ["/a", "/a/b", "/b", "/b/d"]
        test_topic_states = ["NONE|", "OK|ok", "ERR|system failure"]
        while 1:
            for test_topic in test_topics:
                for test_topic_state in test_topic_states:
                    await center_prx.publish(test_topic, test_topic_state)
                    await asyncio.sleep(5)
    elif test_type == "test-subscriber":
        print "topics:", center_prx.getTopicPathes()
        print "topic states:"
        for topic in center_prx.getTopicPathes():
            print topic, "-->", await center_prx.getTopicState(topic)
            print "start listening"

        obj = TopicSubscriberI()
        obj_id = str(uuid.uuid1())
        ws_handle.add_object(obj_id, obj)
        await center_prx.subscribe(obj_id)
    else:
        raise Exception("unknown test_type %s" % test_type)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
            

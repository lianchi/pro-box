import Queue
myqueue = Queue.Queue(20)
data={"asd":"adsf"}
myqueue.put(data)
myqueue.put(data)
myqueue.put(data)
myqueue.put(data)

while True:
    try:
        data = myqueue.get_nowait()
        print data
    except Queue.Empty:
        break

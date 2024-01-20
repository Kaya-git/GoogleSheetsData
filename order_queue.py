class Queue:
    def __init__(self):
        self.items = []  # [3,2,1]

    async def isEmpty(self):
        return self.items == []

    async def enqueue(self, item):
        self.items.insert(0, item)

    async def dequeue(self):
        return self.items.pop()

    async def size(self):
        return len(self.items)


order_queue = Queue()

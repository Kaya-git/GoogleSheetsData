class Queue:
    def __init__(self):
        self.items = []  # [3,2,1]

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)


order_queue = Queue()

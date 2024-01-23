from order_queue import Queue
import pytest
from contextlib import nullcontext as does_not_raise


class Test_Queue:

    @pytest.mark.asyncio
    async def test_isEmpty(self):
        res = True
        assert await Queue().isEmpty() == res

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "x, res, expectation",
        [
            (1, None, does_not_raise())
        ]
    )
    async def test_enqueue(self, x, res, expectation):
        with expectation:
            assert await Queue().enqueue(x) == res

    @pytest.mark.asyncio
    async def test_dequeue(self):
        res = 1
        assert await Queue().dequeue() == res

    @pytest.mark.asyncio
    async def test_size(self):
        res = 1
        assert await Queue().size() == res

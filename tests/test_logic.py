import pytest
from logic import (
    sort_by_x,
    check_list_length,
    list_is_empty,
    ident_values,
    compare_lists
)
from contextlib import nullcontext as does_not_raise


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value_list, res, expectation",
    [
        (
            [
                [1, 2, 3]
            ], [
                [1, 2, 3]
            ], does_not_raise()
        ), (
            [[1, "Х", 3]], [], does_not_raise()
        ), (
            [], [], does_not_raise()
        ), (
            None, [], pytest.raises(TypeError)
        )
    ]
)
async def test_sort_by_x(value_list, res, expectation):
    with expectation:
        assert await sort_by_x(value_list) == res


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "latest_list, current_list, res, expactation",
    [
        (
            [1, 2, 3], [4, 5, 6], {"status": "equal"}, does_not_raise()
        ), (
            [1, 2], [1, 2, 3], {"status": "current_is_bigger"}, does_not_raise()
        ), (
            [1, 2, 3], [1, 2], {"status": "latest_is_bigger"}, does_not_raise()
        ), (
            [], [], {"status": "equal"}, does_not_raise()
        ), (
            None, [], {"status": "equal"}, pytest.raises(TypeError)
        )
    ]
)
async def test_check_list_length(latest_list, current_list, res, expactation):
    with expactation:
        assert await check_list_length(latest_list, current_list) == res


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "req_list, res, expactation",
    [
        (
            [], True, does_not_raise()
        ), (
            [1, 2], False, does_not_raise()
        ), (
            None, False, pytest.raises(TypeError)
        )
    ]
)
async def test_list_is_empty(req_list, res, expactation):
    with expactation:
        assert await list_is_empty(req_list) == res


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "latest_list, current_list, stop_index, res, expactation",
    [
        (
            [[1, 2, 3]],
            [[1, 2, 3]],
            len([[1, 2, 3]]),
            True,
            does_not_raise()
        ), (
            [[1, 2, 3], [3, 4, 5]],
            [[1, 2, 3], [4, 5, 6]],
            len([[1, 2, 3], [3, 4, 5]]),
            False,
            does_not_raise()
        ), (
            [[1, 2, 3], [3, 4, 5], [6, 7, 8]],
            [[1, 2, 3], [3, 4, 5], [7, 9, 10], [11, 23, 55]],
            len([[1, 2, 3], [3, 4, 5], [6, 7, 8]]),
            False,
            does_not_raise()
        ), (
            [[1, 2], [3, 4]],
            [[1, 2], [4, 3]],
            len([[1, 2], [3, 4]]),
            False,
            does_not_raise()
        ), (
            [[1, 2], [4, 3]],
            [[1, 2], [4, 3]],
            len([[1, 2], [4, 3]]),
            True,
            does_not_raise()
        )
    ]
)
async def test_ident_values(
    latest_list, current_list,
    stop_index, res, expactation
):
    with expactation:
        assert await ident_values(
            latest_list, current_list, stop_index
        ) == res


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "latest, current, res, expactation",
    [
        (
            [],
            [],
            {
                "status": "Next round"
            },
            does_not_raise()
        ), (
            [[1, 2]],
            [],
            {
                "status": "Write new"
            },
            does_not_raise()
        ), (
            [],
            [[1, 2]],
            {
                "status": "Del prev"
            },
            does_not_raise()
        ), (
            [[1, 2], [3, 4], [5, 6]],
            [[1, 2], [3, 4]],
            {
                "status": "Del prev, write new"
            },
            does_not_raise()
        ), (
            [[1, 2], [3, 4]],
            [[1, 2], [3, 4], [5, 6]],
            {
                "status": "Del prev, write new"
            },
            does_not_raise()
        ), (
            [[1, 2], [3, 4]],
            [[1, 2], [4, 3]],
            {
                "status": "Del prev, write new"
            },
            does_not_raise()
        ), (
            [[1, 2], [3, 4]],
            [[1, 2], [3, 4]],
            {
                "status": "Next round"
            },
            does_not_raise()
        )
    ]
)
async def test_compare_lists(latest, current, res, expactation):
    with expactation:
        assert await compare_lists(latest, current) == res

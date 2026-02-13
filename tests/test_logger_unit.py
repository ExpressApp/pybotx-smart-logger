from datetime import datetime

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from pybotx_smart_logger import log_levels
from pybotx_smart_logger.contextvars import (
    clear_accumulated_logs,
    get_accumulated_logs,
    set_debug_enabled,
    set_grouping_enabled,
)
from pybotx_smart_logger.logger import (
    flush_accumulated_logs,
    flush_log_entry,
    smart_log,
)
from tests.factories import LogEntryFactory


@pytest.fixture(autouse=True)
def reset_context() -> None:
    clear_accumulated_logs()
    set_debug_enabled(False)
    set_grouping_enabled(False)


@pytest.mark.parametrize(
    ("debug", "group", "expected_buffered", "expected_flush_calls"),
    [
        pytest.param(False, False, 1, 0, id="debug-off"),
        pytest.param(True, False, 0, 1, id="debug-on-no-group"),
        pytest.param(True, True, 1, 0, id="debug-on-group"),
    ],
)
def test_smart_log_behaviour(
    debug: bool,
    group: bool,
    expected_buffered: int,
    expected_flush_calls: int,
    mocker: MockerFixture,
) -> None:
    set_debug_enabled(debug)
    set_grouping_enabled(group)
    flush_log_entry_mock = mocker.patch("pybotx_smart_logger.logger.flush_log_entry")

    with freeze_time("2026-01-02 03:04:05"):
        smart_log("diagnostic", 1, foo="bar")

    buffered_logs = get_accumulated_logs()
    assert len(buffered_logs) == expected_buffered
    assert flush_log_entry_mock.call_count == expected_flush_calls

    if expected_flush_calls:
        flushed_entry, flushed_level = flush_log_entry_mock.call_args.args
        assert flushed_level == log_levels.INFO
        assert flushed_entry.log_message == "diagnostic"
        assert flushed_entry.log_args == (1,)
        assert flushed_entry.log_kwargs == {"foo": "bar"}
    else:
        buffered_entry = buffered_logs[0]
        assert buffered_entry.log_message == "diagnostic"
        assert buffered_entry.time == datetime(2026, 1, 2, 3, 4, 5)


def test_flush_accumulated_logs_flushes_all_and_clears_buffer(
    mocker: MockerFixture,
) -> None:
    entries = LogEntryFactory.build_batch(3)
    get_accumulated_logs().extend(entries)

    flush_log_entry_mock = mocker.patch("pybotx_smart_logger.logger.flush_log_entry")
    flush_accumulated_logs(log_levels.ERROR)

    assert flush_log_entry_mock.call_count == 3
    assert [call.args[0] for call in flush_log_entry_mock.call_args_list] == entries
    assert all(
        call.args[1] == log_levels.ERROR for call in flush_log_entry_mock.call_args_list
    )
    assert get_accumulated_logs() == []


def test_flush_log_entry_applies_metadata_patch(
    mocker: MockerFixture,
) -> None:
    log_entry = LogEntryFactory.build(
        module="module_name",
        function="function_name",
        line_number=777,
        time=datetime(2026, 1, 2, 3, 4, 5),
        log_message="Hello",
        log_args=("world",),
        log_kwargs={"foo": "bar"},
    )
    patched_logger = mocker.Mock()
    patch_mock = mocker.patch(
        "pybotx_smart_logger.logger.logger.patch",
        return_value=patched_logger,
    )

    flush_log_entry(log_entry, log_levels.CRITICAL)

    record_updater = patch_mock.call_args.args[0]
    record = {"name": "old", "line": 0, "function": "old", "time": datetime.min}
    record_updater(record)

    assert record["name"] == "module_name"
    assert record["line"] == 777
    assert record["function"] == "function_name"
    assert record["time"] == datetime(2026, 1, 2, 3, 4, 5)
    patched_logger.log.assert_called_once_with(
        log_levels.CRITICAL,
        "Hello",
        "world",
        foo="bar",
    )

from datetime import datetime

import factory

from pybotx_smart_logger.schemas import LogEntry


class LogEntryFactory(factory.Factory):
    class Meta:
        model = LogEntry

    log_message = factory.Faker("sentence")
    log_args = factory.LazyFunction(tuple)
    log_kwargs = factory.LazyFunction(dict)
    module = factory.Faker("slug")
    function = factory.Faker("word")
    line_number = factory.Faker("pyint", min_value=1, max_value=1000)
    time = factory.LazyFunction(datetime.now)

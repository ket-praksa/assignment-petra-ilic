import hat.aio
import hat.event.server.common
import typing
from hat import json
from hat.event.server.module_engine import ModuleEngine
from hat.event.common import Subscription
from hat.aio import Group
from hat.event.server.common import ProcessEvent

json_schema_id = None
json_schema_repo = None

_source_id = 0


async def create(conf: json.Data, engine: ModuleEngine) -> 'Module':
    """
    Creates a new module instance which receives events
    and modifies their event types.

    Args:
        conf: module configuration
        engine: module engine

    Returns:
        new Module instance
    """
    module = Module()

    global _source_id
    module._source = hat.event.server.common.Source(
        type=hat.event.server.common.SourceType.MODULE, name=__name__, id=_source_id
    )
    _source_id += 1

    module._subscription = hat.event.server.common.Subscription(
        [
            ("gateway", "?", "device", "?", "*",),
            ("device", "system"),
        ]
    )
    module._async_group = hat.aio.Group()
    module._engine = engine

    return module


class Module(hat.event.server.common.Module):
    @property
    def async_group(self) -> Group:
        """
        Creates a group controlling resource's lifetime.

        Returns:
            controlling resource's lifetime
        """
        return self._async_group

    @property
    def subscription(self) -> Subscription:
        """
        Creates a subscribed event types filter.

        Returns:
            Subscription: subscribed event types filter
        """
        return self._subscription

    async def create_session(self) -> 'Session':
        """
        Creates a new module session.

        Returns:
            Session: new module session
        """
        return Session(self._engine, self._source, self._async_group.create_subgroup())


class Session(hat.event.server.common.ModuleSession):
    def __init__(self, engine, source, group):
        self._engine = engine
        self._source = source
        self._async_group = group

    @property
    def async_group(self) -> Group:
        """
        Creates a group controlling resource's lifetime.

        Returns:
            controlling resource's lifetime
        """
        return self._async_group

    async def process(self, changes: typing.List[ProcessEvent]) -> typing.Iterable[ProcessEvent]:
        """
        Processes new session process events.

        Args:
            changes: new session process events

        Returns:
            list of processed events
        """
        process = []

        for event in changes:
            e_type = event.event_type

            if e_type == ("device", "system"):
                event_type = ("gateway", "gateway",
                              "device", "device", "system")
            else:
                event_type = ("gui", e_type[-2], e_type[-1])
            process.append(
                self._engine.create_process_event(
                    self._source,
                    hat.event.server.common.RegisterEvent(
                        event_type=event_type,
                        source_timestamp=None,
                        payload=event.payload,
                    ),
                )
            )

        return process

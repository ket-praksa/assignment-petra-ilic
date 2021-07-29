from project.modules import module as m
from hat.event.server import common
import asyncio
import pytest
import hat

pytestmark = pytest.mark.asyncio

class MockEngine:

    def create_process_event(self, source: common.Source, event: common.RegisterEvent):

        return common.ProcessEvent(
            event_id=common.EventId(server=0,instance=0),
            source=source,
            event_type=event.event_type,
            source_timestamp=event.source_timestamp,
            payload=event.payload,
        )


async def test():

    mock_engine = MockEngine()
    module = await m.create(None,mock_engine)
    session = await module.create_session()

    list_of_events = [hat.event.common.Event(
        event_type=("device", "system","gateway","krompir"),
        source_timestamp=None,
        event_id = common.EventId(1,2),
        timestamp = common.Timestamp(0,1),
        payload=hat.event.common.EventPayload(
            type=hat.event.common.EventPayloadType.JSON,
            data="sirko"
        ),
    )]

    processed_event = await session.process(list_of_events)

    expected_event = processed_event[0].event_type

    assert expected_event == ("gui","gateway","krompir")
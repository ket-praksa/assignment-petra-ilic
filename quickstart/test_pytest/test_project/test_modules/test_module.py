from project.modules import module as m
from hat.event.server import common
import asyncio
import pytest
import hat

pytestmark = pytest.mark.asyncio


class MockEngine:

    def create_process_event(self, source: common.Source, event: common.RegisterEvent):
        return common.ProcessEvent(
            event_id=common.EventId(server=0, instance=0),
            source=source,
            event_type=event.event_type,
            source_timestamp=event.source_timestamp,
            payload=event.payload,
        )

@pytest.mark.parametrize('ev_type, payload, expected_ev_type, expected_payload', [
    (("device", "system", "gateway", "krompir"), 'sirko', ("gui", "gateway", "krompir"), 'sirko'),

    (("device", "system", "gateway", "krompir"), 'ferko', ("gui", "gateway", "krompir"), 'ferko')])
async def test_output_events(ev_type, payload, expected_ev_type, expected_payload):
    mock_engine = MockEngine()
    module = await m.create(None, mock_engine)
    session = await module.create_session()

    list_of_events = [hat.event.common.Event(
        event_type=ev_type,
        source_timestamp=None,
        event_id=common.EventId(1, 2),
        timestamp=common.Timestamp(0, 1),
        payload=hat.event.common.EventPayload(
            type=hat.event.common.EventPayloadType.JSON,
            data=payload
        ),
    )]

    processed_event = await session.process(list_of_events)
    processed_event = processed_event[0]

    expected_event = processed_event.event_type

    assert expected_event == expected_ev_type
    assert type(processed_event) == hat.event.server.common.ProcessEvent
    assert processed_event.payload.data == expected_payload

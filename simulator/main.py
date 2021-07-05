import os.path
from pathlib import Path
import asyncio
import click
import datetime
import logging
import pandapower.networks
import random
import sys
import time
import typing

from hat import aio
from hat import json
from hat.drivers import iec104


mlog = logging.getLogger('simulator')

_reference_net = pandapower.networks.example_simple()


async def async_main(conf):
    simulator = Simulator()
    simulator._points = conf['points']
    simulator._spontaneity = conf['spontaneity']

    simulator._srv = await iec104.listen(
        connection_cb=simulator._connection_cb,
        addr=iec104.Address(conf['address']['host'], conf['address']['port']),
        interrogate_cb=simulator._interrogate_cb,
        command_cb=simulator._command_cb)
    simulator._connections = set()

    simulator._net = pandapower.networks.example_simple()

    simulator._async_group = aio.Group()
    simulator._executor = aio.create_executor()
    await simulator._executor(_ext_power_flow, simulator._net)
    state = {}
    for asdu in conf['points']:
        for io in conf['points'][asdu]:
            point_conf = conf['points'][asdu][io]
            table = getattr(simulator._net, point_conf['table'])
            series = table[point_conf['property']]
            state = json.set_(state, [str(asdu), str(io)],
                              Data(value=_104_value(series[point_conf['id']],
                                                    point_conf['type']),
                                   cause=iec104.Cause.INITIALIZED,
                                   timestamp=time.time()))
    simulator._state = state

    simulator._change_queue = aio.Queue()
    simulator._power_flow_queue = aio.Queue()
    simulator._async_group.spawn(simulator._spontaneous_loop)
    simulator._async_group.spawn(simulator._notification_loop)
    simulator._async_group.spawn(simulator._power_flow_loop)

    await simulator.wait_closed()


class Simulator(aio.Resource):

    @property
    def async_group(self):
        return self._async_group

    async def _connection_cb(self, connection):
        self._connections.add(connection)
        connection.async_group.spawn(
            aio.call_on_cancel,
            lambda: self._connections.remove(connection))
        self.async_group.spawn(
            aio.call_on_cancel,
            lambda: self._connections.remove(connection))

    async def _interrogate_cb(self, _, asdu):
        data = self._data_from_state()
        if asdu == 0xFFFF:
            return data
        return [d._replace(cause=iec104.Cause.INTERROGATED_STATION)
                for d in data if d.asdu_address == asdu]

    async def _command_cb(self, _, commands):
        for command in commands:
            if command.action != iec104.Action.EXECUTE:
                mlog.warning('received action %s, only EXECUTE is supported',
                             command.action)
                continue
            conf = self._points[command.asdu_address][command.io_address]
            series = getattr(self._net, conf['table'])[conf['property']]
            if conf['type'] == 'float':
                value = command.value
            elif conf['type'] == 'single':
                value = (True if command.value == iec104.SingleValue.ON
                         else False)
            series[conf['id']] = value
            self._state = json.set_(
                self._state, [str(command.asdu_address),
                              str(command.io_address)],
                Data(value=command.value,
                     cause=iec104.Cause.REMOTE_COMMAND,
                     timestamp=time.time()))
        self._change_queue.put_nowait(None)
        self._power_flow_queue.put_nowait(None)
        return True

    async def _spontaneous_loop(self):
        while True:
            await asyncio.sleep(random.gauss(self._spontaneity['mu'],
                                             self._spontaneity['sigma']))
            choices = []
            for table in ('gen', 'sgen', 'load'):
                for index, _ in getattr(self._net, table).iterrows():
                    if table in ('load', 'sgen'):
                        cols = ('p_mw', 'q_mvar')
                    if table == 'gen':
                        cols = ('p_mw', )
                    else:
                        cols = tuple()
                    for column in cols:
                        choices.append((table, column, index))
            table, column, index = random.choice(choices)
            ref_value = getattr(_reference_net, table)[column][index]
            getattr(self._net, table)[column] = max(
                random.uniform(ref_value * 0.75, ref_value * 1.25), 0)
            self._change_queue.put_nowait(None)
            await asyncio.sleep(1)
            self._change_queue.put_nowait(None)
            self._power_flow_queue.put_nowait(None)

    async def _power_flow_loop(self):
        while True:
            await self._power_flow_queue.get_until_empty()
            await self._executor(_ext_power_flow, self._net)
            for asdu in self._points:
                for io in self._points[asdu]:
                    point_conf = self._points[asdu][io]
                    table = getattr(self._net, point_conf['table'])
                    series = table[point_conf['property']]
                    new_value = _104_value(series[point_conf['id']],
                                           point_conf['type'])
                    old_value = None
                    old_data = json.get(self._state, [str(asdu), str(io)])
                    if old_data:
                        old_value = old_data.value
                    if old_value != new_value:
                        self._state = json.set_(
                            self._state, [str(asdu), str(io)], Data(
                                value=new_value,
                                cause=iec104.Cause.SPONTANEOUS,
                                timestamp=time.time()))

    def _data_from_state(self):
        for asdu_str, substate in self._state.items():
            for io_str, data in substate.items():
                yield _104_data(data, int(asdu_str), int(io_str))

    async def _notification_loop(self):
        data = list(self._data_from_state())
        self._send(data)
        previous = set(data)
        while True:
            await self._change_queue.get()
            data = list(self._data_from_state())
            self._send([d for d in data if d not in previous])
            previous = set(data)

    def _send(self, data):
        for connection in self._connections:
            connection.notify_data_change(data)


class Data(typing.NamedTuple):
    value: iec104.DataValue
    cause: iec104.Cause
    timestamp: float


def _104_data(simulation_data, asdu, io):
    return iec104.Data(asdu_address=asdu,
                       io_address=io,
                       value=simulation_data.value,
                       cause=simulation_data.cause,
                       time=iec104.time_from_datetime(
                           datetime.datetime.utcfromtimestamp(
                               simulation_data.timestamp)),
                       quality=iec104.Quality(*([False] * 5)),
                       is_test=False)


def _104_value(value, type_104):
    if type_104 == 'float':
        return iec104.FloatingValue(value)
    if type_104 == 'single':
        return iec104.SingleValue.ON if value else iec104.SingleValue.OFF
    raise ValueError(f'{type_104}')


def _ext_power_flow(net):
    pandapower.runpp(net)


root_path = Path(os.path.abspath(__file__)).parent.parent
default_conf_path = root_path / 'conf.yaml'


@click.command()
@click.option('--conf-path', type=Path, default=default_conf_path)
def main(conf_path):
    conf = json.decode_file(conf_path)
    aio.init_asyncio()
    aio.run_asyncio(async_main(conf))


if __name__ == '__main__':
    sys.exit(main())

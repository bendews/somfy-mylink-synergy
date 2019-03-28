import json
import logging
import asyncio
import re
from random import randint

_LOGGER = logging.getLogger(__name__)


class SomfyMyLinkSynergy:
    """API Wrapper for the Somfy MyLink device."""

    def __init__(self, system_id, host, port=44100, timeout=3):
        """Create the object with required parameters."""
        self.host = host
        self.port = port
        self.system_id = system_id
        self._timeout = timeout
        self._stream_reader = None
        self._stream_writer = None

    async def scene_list(self):
        """List all Somfy scenes."""
        return await self.command("mylink.scene.list")

    async def scene_run(self, scene_id):
        """Run specified Somfy scene."""
        return await self.command("mylink.scene.run", sceneID=scene_id)

    async def status_info(self, target_id="*.*"):
        """Retrieve info on all Somfy devices."""
        return await self.command("mylink.status.info", targetID=target_id)

    async def status_ping(self, target_id="*.*"):
        """Send a Ping message to all Somfy devices."""
        return await self.command("mylink.status.ping", targetID=target_id)

    async def move_up(self, target_id="*.*"):
        """Format a Move up message and send it."""
        return await self.command("mylink.move.up", targetID=target_id)

    async def move_down(self, target_id="*.*"):
        """Format a Move Down message and send it."""
        return await self.command("mylink.move.down", targetID=target_id)

    async def move_stop(self, target_id="*.*"):
        """Format a Stop message and send it."""
        return await self.command("mylink.move.stop", targetID=target_id)

    async def command(self, method, **kwargs):
        """Format a Somfy JSON API message."""
        params = dict(**kwargs)
        params.setdefault('auth', self.system_id)
        # Set a random message ID
        message_id = randint(0, 1000)
        message = dict(method=method, params=params, id=message_id)
        return await self.send_message(message)

    async def send_message(self, message):
        """Send a Somfy JSON API message and gather response."""
        # Substring to search in response string to signify end of the message
        # MyLink always returns message 'id' as last key so we search for that
        # print(read_until_string)
        # > b'"id":3}'
        message_id_bytes = str(message['id']).encode('utf-8')
        read_until_string = b'"id":'+message_id_bytes+b'}'
        try:
            await self._send_data(message)
            return await self._recieve_data(read_until_string)
        except UnicodeDecodeError as unicode_error:
            _LOGGER.info('Message collision, trying again: %s', unicode_error)
            return await self.send_message(message)

    async def _make_connection(self):
        """Open asyncio socket connection with MyLink device."""
        if self._stream_writer:
            if not self._stream_writer.is_closing():
                _LOGGER.debug('Reusing existing socket connection to %s on %s',
                            self.host, self.port)
                return
        _LOGGER.debug('Opening new socket connection to %s on %s',
                      self.host, self.port)
        conn = asyncio.open_connection(self.host, self.port)
        conn_wait = asyncio.wait_for(conn, timeout=self._timeout)
        try:
            self._stream_reader, self._stream_writer = await conn_wait
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError) as timeout_err:
            _LOGGER.error('Connection failed for %s on %s. '
                          'Please ensure device is reachable.',
                          self.host, self.port)
            raise timeout_err

    async def _send_data(self, data):
        """Send data to MyLink using JsonRPC via Socket."""
        await self._make_connection()
        try:
            data_as_bytes = str.encode(json.dumps(data))
            self._stream_writer.write(data_as_bytes)
            await self._stream_writer.drain()
        except TypeError as data_error:
            _LOGGER.error('Invalid data sent to device')
            raise data_error

    async def _close_socket(self):
        """Close Socket connection."""
        self._stream_writer.close()
        await self._stream_writer.wait_closed()

    async def _recieve_data(self, read_until=None):
        """Recieve Data from MyLink using JsonRPC via Socket."""
        await self._make_connection()
        try:
            if read_until:
                reader = self._stream_reader.readuntil(read_until)
            else:
                reader = self._stream_reader.read(1024)
            data_bytes = await asyncio.wait_for(reader, timeout=self._timeout)
            data_text = data_bytes.decode('utf-8')
            if "keepalive" in data_text:
                data_text = re.sub('({[a-zA-Z.\":]*keepalive.*?})', '', data_text)
            data_dict = json.loads(data_text)
            return data_dict
        except asyncio.TimeoutError as timeout_err:
            _LOGGER.error('Recieved timeout whilst waiting for'
                          ' response from MyLink device.')
            raise timeout_err
        except UnicodeDecodeError as unicode_error:
            _LOGGER.error('Could not decode Unicode: %s', data_bytes)
            raise unicode_error
        except json.decoder.JSONDecodeError as json_error:
            _LOGGER.error('Could not decode JSON: %s', data_bytes)
            raise json_error
        finally:
            await self._close_socket()

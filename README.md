[![Build Status](https://travis-ci.org/bendews/somfy-mylink-synergy.svg?branch=master)](https://travis-ci.org/bendews/somfy-mylink-synergy)

# Somfy MyLink Synergy API

Python API to utilise the Somfy Synergy API utilising JsonRPC.

## Requirements

- Python >= 3.5.2

## Usage
```python

import asyncio
from somfy_mylink_synergy import SomfyMyLinkSynergy

loop = asyncio.get_event_loop()
mylink = SomfyMyLinkSynergy('YourSystemID', '10.1.1.50')


mylink_covers = loop.run_until_complete(mylink.status_info())
for device in mylink_covers['result']:
    print(device['targetID'], device['name'])

# ('CC0000A.1', 'Bedroom Cover')
# ('CC0000A.2', 'Kitchen Cover')

mylink_scenes = loop.run_until_complete(mylink.scene_list())
for scene in mylink_scenes['result']:
    print(scene['sceneID'], scene['name'])

# ('123456789', 'Morning')
# ('987654321', 'Evening')

mylink_ping = loop.run_until_complete(mylink.status_ping())
for device in mylink_ping['result']:
    print(device)

# ('CC0000A.1')
# ('CC0000A.2')

open_cover = loop.run_until_complete(mylink.move_up('CC0000A.1'))
close_cover = loop.run_until_complete(mylink.move_down('CC0000A.1'))
stop_cover = loop.run_until_complete(mylink.move_stop('CC0000A.1'))
activate_scene = loop.run_until_complete(mylink.scene_run('123456789'))

```


## TODO:

- None

## License

MIT

## Author Information

Created in 2018 by [Ben Dews](https://bendews.com)
# PyBot on Python 3

PyBot exposes the USB4Butia drivers through a TCP server. It also includes the
Chotox simulator, which can be used without a physical robot.

## Running from this repository

Install Python 3 and PyUSB (Debian/Ubuntu package `python3-usb`), then run these
commands from the repository root:

```sh
python3 turtlebots/pybot/pybot_server.py chotox
```

For a physical robot, omit `chotox`. USB access permissions must be configured
for the connected board; the project's udev rules are in `turtlebots/rules`.

In another terminal:

```sh
python3 turtlebots/pybot/pybot_client.py localhost 2009
```

Try `HELP`, `LIST`, `BUTIA_COUNT`, `DESCRIBE` or `CALL admin getVersion`.
`QUIT` closes the server and its connected clients.

## TCP protocol

Requests and responses are UTF-8 lines terminated by `\n`. The server buffers
partial requests and processes multiple lines received together. A request may
contain at most 65536 bytes before its newline. Connections with oversized
requests or invalid UTF-8 are closed. Unknown commands receive an explanatory
response; command execution errors receive `-1`.

The client waits for a complete response, including responses larger than
1024 bytes. `CLIENTS` lists addresses separated by `; ` on one line so it does
not leave extra response lines pending for subsequent commands.

The client defaults to a five-second connection/socket timeout. Pass
`timeout=...` to `robot()` to change it, or `timeout=None` for blocking sockets.
Timeouts and incomplete responses discard the connection and return `-1`.
Commands are not automatically replayed after a connection failure.


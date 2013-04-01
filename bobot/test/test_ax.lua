#!/usr/bin/lua

local socket = require("socket")

--local host, port = "192.168.10.1", 2009
local host, port = "localhost", 2009

local client = assert(socket.connect(host, port))
client:settimeout(nil) --blocking

local function send(s)
--	print("sending", s)
	client:send(s.."\n")
	local ret = client:receive()
--	print("ret:", ret)
	return ret
end

while true do
    print (send("CALL ax sendPacket 1 1"))
    socket.sleep(0.5)
end


--[[
bobot library

Example usage:
	bobot=require("bobot")
	bobot.init()

init() can receive a list of connectors to use. Supported values are "usb", "serial" and "chotox".
For example, to only use de dummy chotox driver, use init({"chotox"})
If no parameter is provided, behaves like init({"usb","serial"}).

--]]

package.path=package.path..";./lib/?.lua"

local socket=require('socket')

B = {}

B.debugprint = print --function() end  --do not print anything by default

--baseboards[iSerial] = BaseBoard
--B.baseboards = {}

--Returns number of baseboards detected.
B.init = function  ( comms )
<<<<<<< HEAD
	if not comms or #comms==0 then comms = {"usb","serial"} end
=======
	if not comms or #comms=0 then comms or {"usb","serial"} end
>>>>>>> origin/master

	B.baseboards={} --flush the baseboard because this function could be call after hardware remove or adition

	local n_boards, n_boards_total = {}, 0

	repeat
		for _, comm in ipairs(comms) do
			B.debugprint ("Querying for baseboards:", comm)
			local comm_lib = require('comms_'..comm)
			if not comm_lib then
				B.debugprint("Could not open library:", comm)
			else
				n_boards[comm] = comm_lib.init(B.baseboards)
				n_boards_total = n_boards_total + n_boards[comm]
			end
		end
		if n_boards_total == 0 then socket.sleep(2) end
	until n_boards_total > 0    
	
	return n_boards_total
end

--B.init()

return B

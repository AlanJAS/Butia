#!/bin/lua
--require "socket"

local butialo=require "butialo"

--local devices = butialo.bobot_devices

local adevices = {}

for _, d in ipairs(devices) do
	adevices[#adevices+1] = d.name
end

table.sort(adevices)

for _, module in ipairs(adevices) do
	device = devices[module]
	--print('///', device)
	--for k,v in pairs(device) do print ('***', k, v) end
	if device.api then 
		print(module, "Y")
		for func, desc in pairs(device.api) do
			local nparams=#desc.parameters
			local generator = func.."( "
			local comma=""
			for i=1,nparams do
				generator=generator..comma..(desc.parameters[i].rname or "p"..i) --parameters
				comma=","
			end
			generator=generator.." )"
			print ('>',generator)
		end
	end
end


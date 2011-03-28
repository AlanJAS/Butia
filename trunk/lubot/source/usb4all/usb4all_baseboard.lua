#!/usr/bin/lua

module(..., package.seeall);

local usb4all_device = require("usb4all_device")

local NULL_BYTE				= string.char(0x00)
local DEFAULT_PACKET_SIZE 	          	= 0x04
local GET_USER_MODULES_SIZE_COMMAND 		= string.char(0x05)
local GET_USER_MODULE_LINE_COMMAND		= string.char(0x06)
local GET_LINES_RESPONSE_PACKET_SIZE 		= 6
local GET_LINE_RESPONSE_PACKET_SIZE 		= 12
local ADMIN_HANDLER_SEND_COMMAND 		= string.char(0x00)
local ADMIN_MODULE_IN_ENDPOINT		= 0x01
local ADMIN_MODULE_OUT_ENDPOINT        	= 0x81
local GET_USER_MODULE_LINE_PACKET_SIZE 	= 0x05
local CLOSEALL_BASE_BOARD_COMMAND         	= string.char(0x07) 
local CLOSEALL_BASE_BOARD_RESPONSE_PACKET_SIZE	= 5
local TIMEOUT	= 1000 --ms

BaseBoard = {}

--Instantiates BaseBoard object.
--Loads list of modules installed on baseboard
function BaseBoard:new(bb)
	--parameters sanity check
	assert(type(bb)=="table")
	assert(type(bb.libusb_handler)=="userdata")

	--OO boilerplate
   	setmetatable(bb, self)
	self.__index = self

	bb.devices = {}
	--read modules list
	local n_modules=bb:get_user_modules_size()
	for i=1, n_modules do
		local name=bb:get_user_module_line(i)
		assert(name)
		local d = usb4all_device.Device:new({name=name, baseboard=bb}) -- in_endpoint=0x01, out_endpoint=0x01})
		bb.devices[name]=d
	end	

	bb:force_close_all()
	return bb
end

--Closes all modules opened on baseboard
function BaseBoard:close()
	--state sanity check
	assert(type(self.devices)=="table")

	for _,d in pairs(self.devices) do
		if type(d.handler)=="number" then
			print ("closing", d.name, d.handler)
			d:close()
		end
	end

	--TODO actually close the baseboard
end

--returns number of modules present on baseboard
function BaseBoard:get_user_modules_size()
	--state sanity check
	assert(type(self.libusb_handler)=="userdata")

	local libusb_handler=self.libusb_handler

	-- In case of get_user_modules_size command is atended by admin module in handler 0 and send operation is 000

	local handler_packet = ADMIN_HANDLER_SEND_COMMAND .. string.char(DEFAULT_PACKET_SIZE) .. NULL_BYTE
	local admin_packet = GET_USER_MODULES_SIZE_COMMAND
	local get_user_modules_size_packet  = handler_packet .. admin_packet    

	local write_res = libusb.bulk_write(libusb_handler, ADMIN_MODULE_IN_ENDPOINT, get_user_modules_size_packet, TIMEOUT)
    	if write_res then
         	local data, err = libusb.bulk_read(libusb_handler, ADMIN_MODULE_OUT_ENDPOINT, 
							GET_LINES_RESPONSE_PACKET_SIZE, TIMEOUT)
		local user_modules_size = string.byte(data, 5)	
		return user_modules_size
	else	
         	print("u4b:get_user_modules_size:libusb write error", write_res)
    	end
end

--returns thename of a given (by a 1-based index)module 
function BaseBoard:get_user_module_line(index)
	--state & parameter sanity check
	assert(type(index)=="number")
	assert(index>0)	
	assert(type(self.libusb_handler)=="userdata")


	local libusb_handler=self.libusb_handler

	-- In case of get_user_module_line command is atended by admin module in handler 0 and send operation is 000
	local get_user_module_line_packet_length = string.char(GET_USER_MODULE_LINE_PACKET_SIZE)
	local handler_packet = ADMIN_HANDLER_SEND_COMMAND .. get_user_module_line_packet_length .. NULL_BYTE
	local admin_packet = GET_USER_MODULE_LINE_COMMAND .. string.char(index-1)
	local get_user_module_line_packet  = handler_packet .. admin_packet

	local write_res = libusb.bulk_write(libusb_handler, ADMIN_MODULE_IN_ENDPOINT, get_user_module_line_packet, TIMEOUT)
    	if write_res then
		local data, err = libusb.bulk_read(libusb_handler, ADMIN_MODULE_OUT_ENDPOINT, 
							GET_LINE_RESPONSE_PACKET_SIZE, TIMEOUT)

		--the name is between a header and a null
		local end_mark = string.find(data, "\000", GET_USER_MODULE_LINE_PACKET_SIZE, true)
		if not end_mark then
			print ("u4b:get_user_module_line:Error parsing module name")
			return
		end
		local module_name = string.sub(data, GET_USER_MODULE_LINE_PACKET_SIZE, end_mark-1)
		return module_name
	else	
		print("u4b:get_user_module_line:libusb write error", write_res)
	end
end

-- resets the baseboard, after this operation the baseboard will claim reenumeration to the operative system
function BaseBoard:close_all()
	for d_name,d in pairs(self.devices) do
		--print ("===", d.name,d.handler)
		if d.handler then d:close() end
	end
end

function BaseBoard:reset()
	--state & parameter sanity check
	assert(type(self.libusb_handler)=="userdata")
	
	local libusb_handler=self.libusb_handler
	-- In case of reset_base_board command is atended by admin module in handler 0 and send operation is 000
	local handler_packet = ADMIN_HANDLER_SEND_COMMAND .. string.char(DEFAULT_PACKET_SIZE) .. NULL_BYTE
	local admin_packet = string.char(0xFF)  --CLOSEALL_BASE_BOARD_COMMAND
	local reset_base_board_packet  = handler_packet .. admin_packet

	local write_res = libusb.bulk_write(libusb_handler, ADMIN_MODULE_IN_ENDPOINT, reset_base_board_packet, TIMEOUT)
    	if write_res then
		-- no tego que leer respuesta porque se reseteo
		--libusb.close(libusb_handler)
		--self.libusb_handler=nil
		--for d_name,d in pairs(self.devices) do
			--print ("===", d.name,d.handler)
		--	d.handler=nil
		--end
	else	
		print("u4b:reset:libusb write error", write_res)
	end
end

function BaseBoard:force_close_all()
	--state & parameter sanity check
	assert(type(self.libusb_handler)=="userdata")
	
	local libusb_handler=self.libusb_handler
	-- In case of reset_base_board command is atended by admin module in handler 0 and send operation is 000
	local handler_packet = ADMIN_HANDLER_SEND_COMMAND .. string.char(DEFAULT_PACKET_SIZE) .. NULL_BYTE
	local admin_packet = CLOSEALL_BASE_BOARD_COMMAND
	local reset_base_board_packet  = handler_packet .. admin_packet

	local write_res = libusb.bulk_write(libusb_handler, ADMIN_MODULE_IN_ENDPOINT, reset_base_board_packet, TIMEOUT)
    	if write_res then
		local data, err = libusb.bulk_read(libusb_handler, ADMIN_MODULE_OUT_ENDPOINT,
					CLOSEALL_BASE_BOARD_RESPONSE_PACKET_SIZE, TIMEOUT)
		if err then
			print("u4b:force_close_all:libusb read error",err)
		else
			print("u4b:force_close_all:libusb read",string.byte(data,1,string.len(data)))
		end
		for d_name,d in pairs(self.devices) do
			--print ("===", d.name,d.handler)
			d.handler=nil
		end
	else	
		print("u4b:force_close_all:libusb write error", write_res)
	end
end


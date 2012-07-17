local device = _G

local RD_VERSION=string.char(0x00)
local string_byte=string.byte

-- description: lets us know button module's version
api={}
api.getVersion = {}
api.getVersion.parameters = {} -- no input parameters
api.getVersion.returns = {[1]={rname="version", rtype="int"}}
api.getVersion.call = function ()
	device:send(RD_VERSION) -- operation code 0 = get version
    local version_response = device:read(3) -- 3 bytes to read (opcode, data)
    if not version_response or #version_response~=3 then return -1 end
    local raw_val = (string_byte(version_response,2) or 0) + (string_byte(version_response,3) or 0)* 256
    return raw_val
end



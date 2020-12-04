local TURTLE = 3000
local PHONE = 4000

modem = peripheral.wrap('top')
local size = vector.new()

if #arg == 3 then
  size.x = tonumber(arg[1])
  size.y = tonumber(arg[2])
  size.z = tonumber(arg[3])
else
  error('no size provided')
end

local target = vector.new(gps.locate())
local payloadMessage = string.format('%d %d %d %d %d %d %d',
  target.x, target.y - 1, target.z,
  size.x, size.y, size.z,
  0
)

print(string.format('targeting %d %d %d', target.x, target.y, target.z))
modem.transmit(TURTLE, PHONE, payloadMessage)

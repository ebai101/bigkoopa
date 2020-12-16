Sock = http.websocket('ws://localhost:8765')
ShouldStop = false

local function processMessage(message)
  if      message == 'forward'  then return turtle.forward()
  elseif  message == 'back'     then return turtle.back()
  elseif  message == 'up'       then return turtle.up()
  elseif  message == 'down'     then return turtle.down()
  elseif  message == 'left'     then return turtle.turnLeft()
  elseif  message == 'right'    then return turtle.turnRight()

  elseif  message == 'exit'     then
    ShouldStop = true
    Sock.close()

  else
    if message ~= nil then print('invalid message: '..message) end
    return false
  end
end

Sock.send('connected')
while not ShouldStop do
  local message = Sock.receive(3)
  local response = processMessage(message)
  if not ShouldStop then Sock.send(response) end
end

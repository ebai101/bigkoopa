local url = 'https://raw.githubusercontent.com/ebai101/minecraftbots/master/minebot.lua'

local function start()
  local directions = {'front', 'back', 'left', 'right'}
  for i = 1, #directions do
    peripheral.call(directions[i], 'wget run ' .. url)
  end
end


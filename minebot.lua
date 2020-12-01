turtle = nil

local SLOT_COUNT = 16
local d = 1
local width, depth = 10, 10
if (#arg == 3) then
  width = tonumber(arg[1])
  depth = tonumber(arg[2])
else
  print('invalid size given, defaulting to 10x10')
end

DROPPED_ITEMS = {
  'minecraft:stone',
  'minecraft:dirt',
  'minecraft:cobblestone',
  'minecraft:sand',
  'minecraft:gravel',
  'minecraft:redstone',
  'minecraft:flint',
  'railcraft:ore_metal',
  'extrautils2:ingredients',
  'minecraft:dye',
  'thaumcraft:nugget',
  'thaumcraft:crystal_essence',
  'thermalfoundation:material',
  'projectred-core:resource_item',
  'thaumcraft:ore_cinnabar',
  'deepresonance:resonating_ore',
  'forestry:apatite'
}

local function dropItems()
  print("Purging Inventory...")
  for slot = 1, SLOT_COUNT, 1 do
    local item = turtle.getItemDetail(slot)
    if(item ~= nil) then
      for filterIndex = 1, #DROPPED_ITEMS, 1 do
        if(item['name'] == DROPPED_ITEMS[filterIndex]) then
          print('dropping - ' .. item['name'])
          turtle.select(slot)
          turtle.dropDown()
        end
      end
    end
  end
end

local function checkFuel()
  turtle.select(1)
  if(turtle.getFuelLevel() < 50) then
    print('attempting refuel')
    for slot = 1, SLOT_COUNT, 1 do
      turtle.select(slot)
      if(turtle.refuel(1)) then
        return true
      end
    end
    return false
  end
  return true
end

local function nextCol(col)
  if col % 2 == 1 then
    turtle.turnRight()
    digForward()
    turtle.turnRight()
  else
    turtle.turnLeft()
    digForward()
    turtle.turnLeft()
  end
end

local function digForward()
  if turtle.detect() then 
    turtle.dig()
    turtle.forward()
  end
  if turtle.detectUp() then turtle.digUp() end
  if turtle.detectDown() then turtle.digDown() end
end

local function main()
  for col = 1, width do
    for row = 1, depth - 1 do
      if not checkFuel() then
        print('out of fuel')
        return
      end
      digForward()
      print(string.format("Row: %d   Col: %d", row, col))
    end
    if col ~= width then nextCol(col) end
  end
  print('done!')
end

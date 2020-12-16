local SLOT_COUNT = 16
local width, depth = 30, 30

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

local function digForward()
  if turtle.detect() then turtle.dig() end
  turtle.forward()
  if turtle.detectUp() then turtle.digUp() end
  if turtle.detectDown() then turtle.digDown() end
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

local function getEnderIndex()
  for slot = 1, SLOT_COUNT, 1 do
    local item = turtle.getItemDetail(slot)
    if(item ~= nil) then
      if(item["name"] == "enderstorage:ender_storage") then
        return slot
      end
    end
  end
  return nil
end

local function manageInventory()
  dropItems()
  local index = getEnderIndex()
  if(index ~= nil) then
    turtle.select(index)
    turtle.digUp()
    turtle.placeUp()
  end
  -- Chest is now deployed
  for slot = 1, SLOT_COUNT, 1 do
    local item = turtle.getItemDetail(slot)
    if(item ~= nil) then
      if(item["name"] ~= "minecraft:coal_block" and item["name"] ~= "minecraft:coal") then
        turtle.select(slot)
        turtle.dropUp()
      end
    end
  end
  turtle.digUp()
end

-- main
if checkFuel() then
  turtle.turnLeft()
  digForward()
  turtle.turnRight()
else
  print('out of fuel')
  return
end
for col = 1, width + 1 do
  for row = 1, depth - 1 do
    if not checkFuel() then
      print('out of fuel')
      return
    end
    digForward()
    print(string.format("row: %02d col: %02d", row, col))
  end
  if col ~= width + 1 then nextCol(col) end
  manageInventory()
end
print('done!')

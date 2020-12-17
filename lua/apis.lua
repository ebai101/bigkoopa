-- bit = {}
-- function bit.blshift(n, bits) end
-- function bit.brshift(n, bits) end
-- function bit.blogic_rshift(n, bits) end
-- function bit.bxor(m, n) end
-- function bit.bor(m, n) end
-- function bit.band(m, n) end
-- function bit.bnot(n) end

-- colors = {}
-- function colors.combine(color1, color2, ...) end
-- function colors.subtract(colors, color1, color2, ...) end
-- function colors.test(colors, color) end

-- commands = {}
-- function commands.exec(command) end
-- function commands.execAsync(command) end
-- function commands.list() end
-- function commands.getBlockPosition() end
-- function commands.getBlockInfo(x, y, z) end
-- function commands.getBlockInfos(x1, y1, z1, x2, y2, z2) end

disk = {}
function disk.isPresent(side) end
function disk.hasData(side) end
function disk.getMountPath(side) end
function disk.setLabel(side, label) end
function disk.getLabel(side) end
function disk.getID(side) end
function disk.hasAudio(side) end
function disk.getAudioTitle(side) end
function disk.playAudio(side) end
function disk.stopAudio(side) end
function disk.eject(side) end

-- fs = {}
-- function fs.list(path) end
-- function fs.exists(path) end
-- function fs.isDir(path) end
-- function fs.isReadOnly(path) end
-- function fs.getName(path) end
-- function fs.getDrive(path) end
-- function fs.getSize(path) end
-- function fs.getFreeSpace(path) end
-- function fs.makeDir(path) end
-- function fs.move(fromPath, toPath) end
-- function fs.copy(fromPath, toPath) end
-- function fs.delete(path) end
-- function fs.combine(basePath, localPath) end
-- function fs.open(path, mode) end
-- function fs.find(wildcard) end
-- function fs.getDir(path) end
-- function fs.complete(partial_name, path, include_files, include_slashes) end

gps = {}
function gps.locate(timeout, debug) end

-- help = {}
-- function help.path() end
-- function help.setPath(path) end
-- function help.lookup(topic) end
-- function help.topics() end
-- function help.completeTopic(topic_prefix) end

-- http = {}
-- function http.request(url, postData, headers) end
-- function http.get(url, headers) end
-- function http.post(url, postData, headers) end
-- function http.checkURL(url) end

-- keys = {}
-- function keys.getName(code) end

-- multishell = {}
-- function multishell.getCurrent() end
-- function multishell.getCount() end
-- function multishell.launch(environment, program_path, arguments) end
-- function multishell.setFocus(tabID) end
-- function multishell.setTitle(tabID, title) end
-- function multishell.getTitle(tabID) end
-- function multishell.getFocus() end

-- paintutils = {}
-- function paintutils.loadImage(path) end
-- function paintutils.drawImage(image, x, y) end
-- function paintutils.drawPixel(x, y, color) end
-- function paintutils.drawLine(startX, startY, endX, endY, color) end
-- function paintutils.drawBox(startX, startY, endX, endY, color) end
-- function paintutils.drawFilledBox(startX, startY, endX, endY, color) end

-- parallel = {}
-- function parallel.waitForAny(function1, function2, ...) end
-- function parallel.waitForAll(function1, function2, ...) end

peripheral = {}
function peripheral.isPresent(side) end
function peripheral.getType(side) end
function peripheral.getMethods(side) end
function peripheral.call(side, method, ...) end
function peripheral.wrap(side) end
function peripheral.find(type, fnFilter) end
function peripheral.getNames() end

rednet = {}
function rednet.open(side) end
function rednet.close(side) end
function rednet.send(receiverID, message, protocol) end
function rednet.broadcast(message, protocol) end
function rednet.receive(protocolFilter, timeout) end
function rednet.isOpen(side) end
function rednet.host(protocol, hostname) end
function rednet.unhost(protocol, hostname) end
function rednet.lookup(protocol, hostname) end
function rednet.run() end

redstone = {}
function redstone.getSides() end
function redstone.getInput(side) end
function redstone.setOutput(side, value) end
function redstone.getOutput(side) end
function redstone.getAnalogInput(side) end
function redstone.setAnalogOutput(side, strength) end
function redstone.getAnalogOutput(side) end
function redstone.getBundledInput(side) end
function redstone.getBundledOutput(side) end
function redstone.setBundledOutput(side, colors) end
function redstone.testBundledInput(side, color) end

-- settings = {}
-- function settings.set(name, value) end
-- function settings.get(name, default) end
-- function settings.unset(name) end
-- function settings.clear() end
-- function settings.getNames() end
-- function settings.load(path) end
-- function settings.save(path) end

-- shell = {}
-- function shell.exit() end
-- function shell.dir() end
-- function shell.setDir(path) end
-- function shell.path() end
-- function shell.setPath(path) end
-- function shell.resolve(localPath) end
-- function shell.resolveProgram(name) end
-- function shell.aliases() end
-- function shell.setAlias(alias, program) end
-- function shell.clearAlias(alias) end
-- function shell.programs(showHidden) end
-- function shell.getRunningProgram() end
-- function shell.run(command, args1, args2, ...) end
-- function shell.openTab(command, args1, args2, ...) end
-- function shell.switchTab(tabID) end
-- function shell.complete(prefix) end
-- function shell.completeProgram(prefix) end
-- function shell.setCompletionFunction(path, completionFunction) end
-- function shell.getCompletionInfo() end

-- term = {}
-- function term.write(text) end
-- function term.blit(text, text_colors, background_colors) end
-- function term.clear() end
-- function term.clearLine() end
-- function term.getCursorPos() end
-- function term.setCursorPos(x, y) end
-- function term.setCursorBlink(bool) end
-- function term.isColor() end
-- function term.getSize() end
-- function term.scroll(n) end
-- function term.redirect(target) end
-- function term.current() end
-- function term.native() end
-- function term.setTextColor(color) end
-- function term.getTextColor() end
-- function term.setBackgroundColor(color) end
-- function term.getBackgroundColor() end
-- function monitor.setTextScale(scale) end
-- function window.setVisible(visibility) end
-- function window.redraw() end
-- function window.restoreCursor() end
-- function window.getPosition() end
-- function window.reposition(x, y, width, height) end

-- textutils = {}
-- function textutils.slowWrite(text, rate) end
-- function textutils.slowPrint(text, rate) end
-- function textutils.formatTime(time, twentyFourHour) end
-- function textutils.tabulate(table, table2, ...) end
-- function textutils.tabulate(color, color2, ...) end
-- function textutils.pagedTabulate(table, table2, ...) end
-- function textutils.pagedTabulate(color, color2, ...) end
-- function textutils.pagedPrint(text, freeLines) end
-- function textutils.serialize(data) end
-- function textutils.unserialize(serializedData) end
-- function textutils.serializeJSON(data, unquote_keys) end
-- function textutils.urlEncode(urlUnsafeString) end
-- function textutils.complete(partial_name, environment) end

turtle = {}
function turtle.craft(quantity) end
function turtle.forward() end
function turtle.back() end
function turtle.up() end
function turtle.down() end
function turtle.turnLeft() end
function turtle.turnRight() end
function turtle.select(slotNum) end
function turtle.getSelectedSlot() end
function turtle.getItemCount(slotNum) end
function turtle.getItemSpace(slotNum) end
function turtle.getItemDetail(slotNum) end
function turtle.equipLeft() end
function turtle.equipRight() end
function turtle.attack(toolSide) end
function turtle.attackUp(toolSide) end
function turtle.attackDown(toolSide) end
function turtle.dig(toolSide) end
function turtle.digUp(toolSide) end
function turtle.digDown(toolSide) end
function turtle.place(signText) end
function turtle.placeUp() end
function turtle.placeDown() end
function turtle.detect() end
function turtle.detectUp() end
function turtle.detectDown() end
function turtle.inspect() end
function turtle.inspectUp() end
function turtle.inspectDown() end
function turtle.compare() end
function turtle.compareUp() end
function turtle.compareDown() end
function turtle.compareTo(slot) end
function turtle.drop(count) end
function turtle.dropUp(count) end
function turtle.dropDown(count) end
function turtle.suck(amount) end
function turtle.suckUp(amount) end
function turtle.suckDown(amount) end
function turtle.refuel(quantity) end
function turtle.getFuelLevel() end
function turtle.getFuelLimit() end
function turtle.transferTo(slot, quantity) end

-- vector = {}
-- function vector.new(x, y, z) end
-- function vector:add(vectorB) end
-- function vector:sub(vectorB) end
-- function vector:mul(n) end
-- function vector:dot(vectorB) end
-- function vector:cross(vectorB) end
-- function vector:length() end
-- function vector:normalize() end
-- function vector:round() end
-- function vector:tostring() end

-- window = {}
-- function window.create(parentTerm, x, y, width, height, visible) end

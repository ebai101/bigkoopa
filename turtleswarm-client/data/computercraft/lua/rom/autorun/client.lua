argv = {...}

-- pack pcall results into a table
local function pack(status, ...)
	return status, { ... }
end

-- get table length
local function len(table)
	local count = 0
	for _ in pairs(table) do count = count + 1 end
	return count
end

-- main websocket loop
-- recieves a packet, evaluates it and sends a response back
local function loop(ws)
	while true do
		local msg = ws.receive()
		if msg == nil then
			print('lost connection')
			break
		end

		-- decode and execute
		local msg_decoded = json.decode(msg)
		local status, response = pack(pcall(loadstring(msg_decoded['command'])))

		-- parse status and response
		if status == true then
			if response[1] == false then
				status = 1
			else
				status = 0
			end
		else
			status = -1
		end
		if len(response) == 1 then response = response[1] end -- single value responses
		if response == nil then response = 'None' end

		-- send response
		local res_packet = {
					command = msg_decoded['command'],
					status = status,
					result = response,
					nonce = msg_decoded['nonce'],
				}
		print(msg_decoded['command']:gsub("^return ","")..' -> '..tostring(response))
		ws.send(json.encode(res_packet))
	end
end

-- if turtleswarm.ignore is true, do not run the client
-- set this on the command line with "set turtleswarm.ignore true"
if settings.get('turtleswarm.ignore') == true then
	print('turtleswarm.ignore set, exiting')
	return
end

-- only run the program on turtles, not normal computers
if not turtle and not argv[1] then
	return
end

while true do
	term.clear()
	term.setCursorPos(1,1)
	print('turtle ID '..os.getComputerID())
	local ws, ws_err = http.websocket('ws://localhost:42069')

	if ws_err then
		print('failed to initialize websocket:')
		print(ws_err)
	else
		print('connection established')
		local loop_status, loop_err = pcall(loop, ws)

		if loop_err then
			print('websocket loop returned an error: '..loop_err)
		end
		ws.close()
	end

	for i = 1, 5 do
		term.setCursorPos(1,5)
		term.clearLine()
		print('reconnecting in 5 seconds'..string.rep('.', i))
		os.sleep(1)
	end
end

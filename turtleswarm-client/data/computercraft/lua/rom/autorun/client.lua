-- pack pcall results into a table
local function pack(status, ...)
	return status, { ... }
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
		if response == nil then response = 'None' end

		-- send response
		ws.send(json.encode({
					command = msg_decoded['command'],
					status = status,
					result = response,
					nonce = msg_decoded['nonce'],
				}))
	end
end

-- if turtleswarm.ignore is true, do not run the client
-- set this on the command line with "set turtleswarm.ignore true"
if settings.get('turtleswarm.ignore') == true then
	print('turtleswarm.ignore set, exiting')
	return
end

while true do
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

	print('attempting to reconnect in 5 seconds...')
	os.sleep(5)
end

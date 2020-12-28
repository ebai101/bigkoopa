local json = require('json')


local function doEval(obj)
	local func = loadstring(obj['data'])
	local result = func()
	return json.encode({
			turtle_id = obj.turtle_id,
			type = 'eval_r',
			data = result,
			nonce = obj.nonce
		})
end


local function doWakeup(obj)
	local info = {
		comupterId = os.getComputerID(),
		location = { gps.locate() }
	}
	return json.encode({
			turtle_id = obj.turtle_id,
			type = 'wakeup_r',
			data = info,
			nonce = obj.nonce
		})
end


local function websocketLoop()
	local ws, err = http.websocket('localhost:42069')

	if err then
		print(err)
	elseif ws then
		while true do
			term.clear()
			term.setCursorPos(1,1)

			print('waiting for messages...')
			local message = ws.receive()
			if message == nil then
				break
			end

			local obj = json.decode(message)
			if obj.type == 'eval' then
				ws.send(doEval(obj))
			elseif obj.type == 'wakeup' then
				ws.send(doWakeup(obj))
			end
		end
	end
	if ws then
		ws.close()
	end
end


while true do
	local status, res = pcall(websocketLoop)

	term.clear()
	term.setCursorPos(1,1)
	if res == 'Terminated' then
		print('terminating turtle loop')
		break
	end

	print('attempting restart in 5 seconds')
	os.sleep(5)
end

local json = require('json')

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
				local func = loadstring(obj['function'])
				local result = func()
				ws.send(json.encode({data=result, nonce=obj.nonce}))
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

	print('sleeping!')
	os.sleep(5)
end

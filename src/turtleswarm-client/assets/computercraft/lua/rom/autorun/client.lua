local function connect()
	local ws, err = http.websocket('ws://localhost:42069')

	if err then
		print(err)
	elseif ws then
		print('connection established')
		while true do
			local msg = ws.receive()
			if msg == nil then break end

			-- decode and execute
			local obj = json.decode(msg)
			local func = loadstring(obj['data'])
			local res = func()
			print(msg, res)

			-- send response
			ws.send(json.encode({
						data = res,
						nonce = obj['nonce'],
					}))
		end
		ws.close()
	end
end

while true do
	pcall(connect())
	print('attempting to reconnect in 5 seconds...')
	os.sleep(5)
end

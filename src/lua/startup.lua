local json = require('json')

local function doEval(obj)
	local func = loadstring(obj['data'])
	local result = func()
	return json.encode({
			data = result,
			nonce = obj.nonce
		})
end


local function main()
	local ws, err = http.websocket('ws://localhost:42069')

	if err then
		print(err)
	elseif ws then
		while true do
			print('waiting for messages...')
			local message = ws.receive()

			if message == nil then
				print('nil message')
			else
				print(string.format('%q', message))
			end

			-- local obj = json.decode(message)
			-- ws.send(doEval(obj))
		end
	end

	if ws then
		ws.close()
	end
end

main()

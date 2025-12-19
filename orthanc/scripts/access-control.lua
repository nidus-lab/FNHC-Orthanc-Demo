-- Access control for Orthanc with Authorization Plugin
-- This script works in conjunction with the authorization plugin
-- The authorization plugin handles user permissions based on roles
-- This script provides additional logging and basic filtering

-- function IncomingHttpRequestFilter(method, uri, ip, username, httpHeaders)
--     -- Log all requests for monitoring
--     print(string.format("Request: %s %s from IP %s", method, uri, ip))

--     -- Check for API key in headers (used by authorization plugin)
--     local apiKey = httpHeaders['api-key']
--     if apiKey then
--         print(string.format("API Key present: %s...", string.sub(apiKey, 1, 10)))
--     end

--     -- Allow all requests - the authorization plugin will handle permission checks
--     -- based on user roles and permissions defined in permissions.jsonc

--     -- Allow all GET requests (read operations)
--     if method == 'GET' then
--         return true
--     end

--     -- Allow POST requests (including bulk-delete) - authorization plugin will check permissions
--     if method == 'POST' then
--         if uri == '/tools/bulk-delete' then
--             print(string.format("Bulk delete request from IP %s - authorization plugin will check permissions", ip))
--         end
--         return true
--     end

--     -- Allow PUT requests - authorization plugin will check permissions
--     if method == 'PUT' then
--         return true
--     end

--     -- Allow DELETE requests - authorization plugin will check permissions
--     if method == 'DELETE' then
--         print(string.format("DELETE request to %s from IP %s - authorization plugin will check permissions", uri, ip))
--         return true
--     end

--     -- Block other HTTP methods by default
--     print(string.format("Blocked %s request to %s from IP %s", method, uri, ip))
--     return false
-- end

-- Optional: Log when the script is loaded
print("Access control script disabled")
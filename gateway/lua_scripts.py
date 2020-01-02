# modified from here:
# https://medium.com/@sahiljadon/rate-limiting-using-redis-lists-and-sorted-sets-9b42bc192222
RATE_LIMIT = """
--[[
    remove any scores for the at key between 0 and 1 minute before the 
    current request time
]]--
redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, ARGV[1] - 60 * 1000 )

--[[
    check if number of scores in the key are < requests allowed and if so
    add the score to the sorted set
]]--
local num_of_existing_scores = tonumber(redis.call('ZCARD', KEYS[1]))

if num_of_existing_scores < tonumber(ARGV[2])
then
    redis.call('ZADD', KEYS[1], ARGV[1], ARGV[1])
    return num_of_existing_scores..':pass'
else
    return num_of_existing_scores..':limit-exceeded'
end

"""

RATE_LIMIT_QUERY = """
--[[
    remove any scores for the at key between 0 and 1 minute before the 
    current request time
]]--
redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, ARGV[1] - 60 * 1000 )

--[[
    check if number of scores in the key are < requests allowed and if so
    add the score to the sorted set
]]--
return tonumber(redis.call('ZCARD', KEYS[1]))
"""

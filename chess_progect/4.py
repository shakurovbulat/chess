x, y, k, l = map(int, input().split())
start = min(x, y)
end = max(x, y)
lights_needed = 0
position = start
while position + l < end:
    position = ((position + l + k - 1) // k) * k
    lights_needed += 1
print(lights_needed)

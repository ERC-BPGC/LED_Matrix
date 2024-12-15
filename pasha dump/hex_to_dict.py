import json

file = open("colors.txt", "r")
data = file.read().split(", ")
file.close()

twenty = []
main = []
for x in data:
    twenty.append(x)

    if len(twenty) == 20:
        main.append(twenty.copy())
        twenty.clear()

finalDict = {
    main[0][0]: [[0, 0]]
}

for y in range(40):
    for x in range(20):
        k = main[y][x]
        if k in list(finalDict.keys()):
            finalDict[k].append([x, y])
        else:
            finalDict[k] = [[x, y]]

# Save finalDict to JSON file
with open("disp.json", "w") as json_file:
    json.dump(finalDict, json_file)

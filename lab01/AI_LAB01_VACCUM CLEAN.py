room = {}

print("Enter the number of rooms")
m = int(input())

print("Enter the room number and status")

for i in range(m):
    print("Enter the Room Number")
    d = int(input())

    print("Enter the status of the room (clean/dirty)")
    k = input().lower()

    room[d] = k

model = room.copy()

cc = 0
dc = 0

print("\nInitial Room Model:")
print(model)

for i in sorted(model.keys()):

    if cc == m:
        print("All rooms are clean")
        break

    elif model[i] == "dirty":
        print("Room", i, "is dirty")
        print("Cleaning Room", i)

        model[i] = "clean"
        cc = cc + 1

    elif model[i] == "clean":

        keys = sorted(model.keys())
        pos = keys.index(i)

        if pos + 1 < len(keys):
            next_room = keys[pos + 1]

            if model[next_room] == "dirty":
                print("Moving Left")
                dc = dc + 1

        cc = cc + 1

print("\nFinal Room Model:")
print(model)

if all(model[i] == "clean" for i in model):
    print("All rooms are clean")

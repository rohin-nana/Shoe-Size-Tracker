f = open("data.txt", "r")
g = open("genders.txt", "w")

lines = f.readlines()
length = len(lines)
ind = 2
genders = set()
while ind < length:
    if lines[ind].strip() != "":
        genders.add(lines[ind].strip().replace("'", "’"))
    ind += 7

f.close()

for ind, gender in enumerate(genders):
    g.write("{ id: " + str(ind) + ", name: \"" + gender + "\" }," + "\n")

g.close()
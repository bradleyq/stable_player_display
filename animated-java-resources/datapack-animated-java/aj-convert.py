import sys
import nbtlib
import os

nArgs = len(sys.argv)
if nArgs < 2:
    print("usage: aj-convert.py [project] [optional:flags]")
    print("available flags:")
    print("\t-ns=[namespace]\t\tproject namespace. Default 'zzz'")
    print("\t-pn=[playerName]\tplayer skin to use. Default '' no skin, must be set later in game")
    print("\t-s\t\t\tslim model. Default disabled")
    quit()


HEAD = "head"
RARM = "right_arm"
LARM = "left_arm"
TORSO = "torso"
RLEG = "right_leg"
LLEG = "left_leg"

    # name, offset, custom model data
OFFSETS = ((HEAD, 0.0, 1), (RARM, -1024.0, 2), (LARM, -2048.0, 3), (TORSO, -3072.0, 4), (RLEG, -4096.0, 5), (LLEG, -5120.0, 6))
OFFSETS_S = ((HEAD, 0.0, 1), (RARM, -1024.0, 7), (LARM, -2048.0, 8), (TORSO, -3072.0, 4), (RLEG, -4096.0, 5), (LLEG, -5120.0, 6))

offsets = OFFSETS
project = sys.argv[1]
playerName = ""
namespace = "zzz"

if nArgs > 2:
    for arg in sys.argv[2:]:
        if "-ns=" == arg[:4]:
            namespace = arg[4:]
        elif "-pn=" == arg[:4]:
            playerName = arg[4:]
        elif "-s" == arg:
            offsets = OFFSETS_S


print("running aj-convert on project " + project + " with namespace " + namespace)

#construct summon.mcfunction path
summonPath =  os.path.join(".", "data", project, "functions", "summon.mcfunction")
summonResult = ""

# read summon.mcfunction
f = open(summonPath, "r")

temp = f.readline()
nbtStart = temp.index("~ ~ ~ ")
nbtStart += len("~ ~ ~ ")

summonResult += temp[:nbtStart]

nbtRoot = nbtlib.parse_nbt(temp[nbtStart:])

for passenger in nbtRoot["Passengers"]:
    for offsetPair in offsets:
        if "aj." + project + ".bone." + offsetPair[0] in passenger["Tags"]:
            passenger["transformation"][7] += offsetPair[1]
            passenger["item"]["tag"]["CustomModelData"] = nbtlib.tag.Int(offsetPair[2])
            passenger["item_display"] = nbtlib.tag.String("thirdperson_righthand")
            if playerName != "":
                passenger["item"]["id"] = nbtlib.tag.String("minecraft:player_head")
                passenger["item"]["tag"]["SkullOwner"] = nbtlib.tag.String(playerName)
            else:
                passenger["item"]["id"] = nbtlib.tag.String("minecraft:air")

summonResult += nbtlib.serialize_tag(nbtRoot, compact=True) + "\n"
summonResult += f.readline()

f.close()

# # write to summon.mcfunction
f = open(summonPath, "w")
f.write(summonResult)
f.close()

# construct default_as_bone.mcfunction path
defaultBonePath =  os.path.join(".", "data", namespace + "_" + project + "_internal", "functions", "apply_variant", "default_as_bone.mcfunction")
defaultBoneResult = ""

# read default_as_bone.mcfunction
f = open(defaultBonePath, "r")

for line in f:
    for offsetPair in offsets:
        if "aj." + project + ".bone." + offsetPair[0] in line:
            line = line.strip()[:-1] + str(offsetPair[2]) + "\n"
    defaultBoneResult += line

f.close()

# # write to default_as_bone.mcfunction
f = open(defaultBonePath, "w")
f.write(defaultBoneResult)
f.close()

# construct tree path
animationPath = os.path.join(".", "data", namespace + "_" + project + "_internal", "functions", "animations")


for animation in next(os.walk(animationPath))[1]:
    animationTreePath = os.path.join(animationPath, animation, "tree")
    for leafName in next(os.walk(animationTreePath))[2]:
        if ("as_bone" in leafName):
            leafAsBoneResult = ""
            animationLeafPath = os.path.join(animationTreePath, leafName)

            # read leaf
            f = open(animationLeafPath, "r")
            for line in f:
                for offsetPair in offsets:
                    if "aj." + project + ".bone." + offsetPair[0] in line:
                        nbtStart = line.index("merge value ")
                        nbtStart += len("merge value ")

                        tmpLine = line[:nbtStart]

                        nbtRoot = nbtlib.parse_nbt(line[nbtStart:])
                        nbtRoot["transformation"][7] += offsetPair[1]

                        tmpLine += nbtlib.serialize_tag(nbtRoot, compact=True) + "\n"
                leafAsBoneResult += tmpLine
            
            f.close()

            # write leaf
            f = open(animationLeafPath, "w")
            f.write(leafAsBoneResult)
            f.close()

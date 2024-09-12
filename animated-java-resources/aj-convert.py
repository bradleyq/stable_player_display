import sys
import nbtlib
import os

# Constants for offsets and components
HEAD, RARM, LARM, TORSO, RLEG, LLEG = "head", "right_arm", "left_arm", "torso", "right_leg", "left_leg"

OFFSETS = (
    (HEAD, 0.0, 1), (RARM, -1024.0, 2), (LARM, -2048.0, 3),
    (TORSO, -3072.0, 4), (RLEG, -4096.0, 5), (LLEG, -5120.0, 6)
)

OFFSETS_S = (
    (HEAD, 0.0, 1), (RARM, -1024.0, 7), (LARM, -2048.0, 8),
    (TORSO, -3072.0, 4), (RLEG, -4096.0, 5), (LLEG, -5120.0, 6)
)

def parse_arguments():
    """Parse command-line arguments."""
    nArgs = len(sys.argv)
    if nArgs < 2:
        print("Usage: aj-convert.py [project] [optional:flags]")
        print("Available flags:")
        print("\t-pn=[playerName]\tPlayer skin to use. Default '' (no skin), must be set later in game")
        print("\t-s\t\t\tEnable slim model. Default is disabled")
        sys.exit(1)
    
    project = sys.argv[1]
    playerName = ""
    offsets = OFFSETS

    if nArgs > 2:
        for arg in sys.argv[2:]:
            if arg.startswith("-pn="):
                playerName = arg[4:]
            elif arg == "-s":
                offsets = OFFSETS_S

    return project, playerName, offsets

def read_and_modify_summon_function(summonPath, project, offsets, playerName):
    """Read and modify the summon.mcfunction file."""
    summonResult = ""

    try:
        with open(summonPath, "r") as f:
            for _ in range(3):
                summonResult += f.readline()

            temp = f.readline()
            
            if temp[-4] == ',':
                temp = temp[:-4] + temp[-3:]  # Remove malformed last comma

            nbtStart = temp.index("~ ~ ~ ") + len("~ ~ ~ ")
            summonResult += temp[:nbtStart]
            nbt_data = temp[nbtStart:]

            nbtRoot = nbtlib.parse_nbt(nbt_data)
            modify_nbt_passengers(nbtRoot, project, offsets, playerName)

            summonResult += nbtlib.serialize_tag(nbtRoot, compact=True) + "\n"
            summonResult += f.readline()

        with open(summonPath, "w") as f:
            f.write(summonResult)

        print(f"Successfully modified {summonPath}")

    except Exception as e:
        print(f"Error processing {summonPath}: {e}")
        sys.exit(1)

def modify_nbt_passengers(nbtRoot, project, offsets, playerName):
    """Modify NBT data for passengers."""
    for passenger in nbtRoot["Passengers"][1:]:  # Skip First Marker
        for offsetPair in offsets:
            tag = f"aj.{project}.bone.{offsetPair[0]}"
            if tag in passenger["Tags"]:
                passenger["transformation"]["translation"][1] += offsetPair[1]
                passenger["item"]["components"]["minecraft:custom_model_data"] = nbtlib.tag.Int(offsetPair[2])
                passenger["item_display"] = nbtlib.tag.String("thirdperson_righthand")
                
                if playerName:
                    passenger["item"]["id"] = nbtlib.tag.String("minecraft:player_head")
                    passenger["item"]["components"]["profile"] = nbtlib.tag.Compound({"name": nbtlib.tag.String(playerName)})
                else:
                    passenger["item"]["id"] = nbtlib.tag.String("minecraft:air")

def process_mcfunction_files(paths, project, offsets):
    """Process set_default_pose.mcfunction and apply_default_pose.mcfunction files."""
    for path in paths:
        try:
            with open(path, "r") as f:
                lines = f.readlines()

            modifiedLines = []
            for line in lines:
                if "merge entity @s" in line:
                    modifiedLines.append(modify_merge_entity_line(line, project, offsets))
                else:
                    modifiedLines.append(line)

            with open(path, "w") as f:
                f.writelines(modifiedLines)

            print(f"Successfully modified {path}")

        except Exception as e:
            print(f"Error processing {path}: {e}")
            sys.exit(1)

def modify_merge_entity_line(line, project, offsets):
    """Modify a merge entity line with the appropriate offsets."""
    for offsetPair in offsets:
        if f"[tag=aj.{project}.bone.{offsetPair[0]}]" in line:
            nbtStart = line.index("merge entity @s ") + len("merge entity @s ")
            tmpLine = line[:nbtStart]
            nbtRoot = nbtlib.parse_nbt(line[nbtStart:])
            nbtRoot["transformation"][7] += offsetPair[1]
            return tmpLine + nbtlib.serialize_tag(nbtRoot, compact=True) + "\n"
    return line

def modify_animation_frames(rootpath, project, offsets):
    """Modify all animation frames in the specified project."""
    try:
        subfolders = [entry for entry in os.listdir(rootpath) if os.path.isdir(os.path.join(rootpath, entry))]

        for animation in subfolders:
            frames_path = os.path.join(rootpath, animation, "zzz", "frames")
            frames = [entry for entry in os.listdir(frames_path) if os.path.isfile(os.path.join(frames_path, entry))]

            i = 0
            for frame in frames:
                i+=1
                sys.stdout.write(f"\rEditing {animation} frames: [{i}/{len(frames)}]")
                framepath = os.path.join(frames_path, frame)
                modify_frame_file(framepath, offsets)
            print()

    except Exception as e:
        print(f"Error processing animations: {e}")
        sys.exit(1)

def modify_frame_file(framepath, offsets):
    """Modify a single frame file with the appropriate offsets."""
    try:
        with open(framepath, "r") as f:
            lines = f.readlines()

        modifiedLines = []
        for line in lines:
            if ") " in line:
                modifiedLines.append(modify_frame_line(line, offsets))
            else:
                modifiedLines.append(line)

        with open(framepath, "w") as f:
            f.writelines(modifiedLines)

    except Exception as e:
        print(f"Error processing frame {framepath}: {e}")

def modify_frame_line(line, offsets):
    """Modify a line in a frame file with the appropriate offsets."""
    for offsetPair in offsets:
        if offsetPair[0] in line and f"{offsetPair[0]}_down" not in line:
            nbtStart = line.index(") ") + len(") ")
            tmpLine = line[:nbtStart]
            nbtRoot = nbtlib.parse_nbt(line[nbtStart:])
            nbtRoot["transformation"][7] += offsetPair[1]
            return tmpLine + nbtlib.serialize_tag(nbtRoot, compact=True) + "\n"
    return line

def process_default_variant_mcfunction(project, offsets):
    """Process the apply.mcfunction file and update corresponding zzz files."""
    print("Updating default variant")
    apply_mcfunction_path = os.path.join(".", "data", "animated_java", "function", project, "variants", "default", "apply.mcfunction")
    zzz_folder_path = os.path.join(".", "data", "animated_java", "function", project, "variants", "default", "zzz")

    with open(apply_mcfunction_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        # Process the line to extract the bone and the corresponding zzz file number
        if "tag=aj."+ project +".bone." in line and "zzz/" in line:
            parts = line.split()

            bone = ""
            zzz_file_number = ""

            for part in parts:
                if part.startswith("@s[tag=aj." + project + ".bone."):
                    bone = part.split(".")[-1].replace("]", "")
                elif "zzz/" in part:
                    zzz_file_number = part.split("/")[-1]

            if bone and zzz_file_number:
                # Find the correct offset for the bone
                for offset in offsets:
                    if offset[0] == bone:
                        custom_model_data_value = offset[2]
                        zzz_file_path = os.path.join(zzz_folder_path, zzz_file_number + ".mcfunction")
                        print(f"Updating bone {bone} in {zzz_file_number}.mcfunction with custom_model_data {custom_model_data_value}")
                        update_custom_model_data(zzz_file_path, custom_model_data_value)
                        break

def update_custom_model_data(filepath, custom_model_data_value):
    """Update the custom_model_data value in the specified file."""
    with open(filepath, 'r') as file:
        line = file.readline() # Skip first line
        line = file.readline()

    with open(filepath, 'w') as file:
        # Replace the old value with the new custom_model_data_value
        line = f"data modify entity @s item.components.minecraft:custom_model_data set value {custom_model_data_value}\n"
        file.write(line)

def main():
    project, playerName, offsets = parse_arguments()

    print(f"Running aj-convert on project {project}")

    summonPath = os.path.join(".", "data", "animated_java", "function", project, "summon.mcfunction")
    read_and_modify_summon_function(summonPath, project, offsets, playerName)

    mcfunction_paths = [
        os.path.join(".", "data", "animated_java", "function", project, "set_default_pose.mcfunction"),
        os.path.join(".", "data", "animated_java", "function", project, "apply_default_pose.mcfunction")
    ]
    process_mcfunction_files(mcfunction_paths, project, offsets)

    animations_rootpath = os.path.join(".", "data", "animated_java", "function", project, "animations")
    modify_animation_frames(animations_rootpath, project, offsets)

    process_default_variant_mcfunction(project,offsets)

if __name__ == "__main__":
    main()

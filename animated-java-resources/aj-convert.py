import sys
import nbtlib
import os
import re

# Constants for offsets and components
HEAD, RARM, LARM, TORSO, RLEG, LLEG = "head", "right_arm", "left_arm", "torso", "right_leg", "left_leg"

OFFSETS = (
    (HEAD, 0.0), (RARM, -1024.0), (LARM, -2048.0),
    (TORSO, -3072.0), (RLEG, -4096.0), (LLEG, -5120.0)
)

OFFSETS_S = (
    (HEAD, 0.0), (RARM, -1024.0), (LARM, -2048.0),
    (TORSO, -3072.0), (RLEG, -4096.0), (LLEG, -5120.0)
)

def parse_arguments():
    """Parse command-line arguments."""
    nArgs = len(sys.argv)
    if nArgs < 2:
        print("Usage: aj-convert.py [project] [optional:flags]")
        print("Available flags:")
        print("\t-pn=[playerName]\tPlayer skin to use. Default '' (no skin), must be set later in game")
        sys.exit(1)
    
    project = sys.argv[1]
    playerName = ""
    offsets = OFFSETS

    if nArgs > 2:
        for arg in sys.argv[2:]:
            if arg.startswith("-pn="):
                playerName = arg[4:]

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
                passenger["item"]["components"]["minecraft:item_model"] = nbtlib.tag.String("player_display:player/" + offsetPair[0])
                passenger["item_display"] = nbtlib.tag.String("thirdperson_righthand")
                
                if playerName:
                    passenger["item"]["id"] = nbtlib.tag.String("minecraft:player_head")
                    passenger["item"]["components"]["profile"] = nbtlib.tag.Compound({"name": nbtlib.tag.String(playerName)})
                else:
                    passenger["item"]["id"] = nbtlib.tag.String("minecraft:air")

def process_pose_files(paths, project, offsets):
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
    zzz_folder_path = os.path.join(".", "data", "animated_java", "function", project, "variants", "default", "zzz")

    # Loop through each .mcfunction file in the zzz folder
    for file in os.listdir(zzz_folder_path):
        file_path = os.path.join(zzz_folder_path, file)
        
        # Read all lines
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Write the modified lines back to the file
        with open(file_path, 'w') as file:
            file.writelines(modify_variant_line(lines[1])) # Update the second line

def modify_variant_line(line):
    # Extract the last part after the last "/" using regex
    match = re.search(r'([^/]+)"$', line)
    if match:
        last_name = match.group(1)  # Get the last part after the last "/"
        # Modify the line with the new format
        return f'data modify entity @s item.components.minecraft:item_model set value "player_display:player/{last_name}"\n'
    return line

def generate_slim_variant(project):
    """Copy the 'default' folder to 'slim', update 'apply.mcfunction' references, and modify zzz files."""
    
    # Define paths for 'default' and 'slim'
    base_path = os.path.join(".", "data", "animated_java", "function", project, "variants")
    default_folder_path = os.path.join(base_path, "default")
    slim_folder_path = os.path.join(base_path, "slim")
    
    # Copy 'default' folder to 'slim'
    os.makedirs(slim_folder_path, exist_ok=True)
    
    # Copy all files and subdirectories from 'default' to 'slim'
    for root, dirs, files in os.walk(default_folder_path):
        relative_path = os.path.relpath(root, default_folder_path)
        target_dir = os.path.join(slim_folder_path, relative_path)
        os.makedirs(target_dir, exist_ok=True)
        
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(target_dir, file)
            with open(src_file, 'rb') as f_src, open(dest_file, 'wb') as f_dest:
                f_dest.write(f_src.read())
    
    # Modify 'apply.mcfunction' file in the 'slim' folder
    apply_file_path = os.path.join(slim_folder_path, "apply.mcfunction")
    
    if os.path.isfile(apply_file_path):
        with open(apply_file_path, 'r') as file:
            content = file.read()
        
        # Replace "default" with "slim" in the content
        modified_content = content.replace("default/zzz","slim/zzz")
        
        # Write the modified content back to the file
        with open(apply_file_path, 'w') as file:
            file.write(modified_content)

    # Modify files in 'zzz' folder in 'slim'
    zzz_folder_path = os.path.join(slim_folder_path, "zzz")
    
    for filename in os.listdir(zzz_folder_path):
        if filename.endswith(".mcfunction"):
            file_path = os.path.join(zzz_folder_path, filename)
            
            # Read the file and check the last line
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            if lines:
                # Check if the last line contains "right_arm" or "left_arm"
                if lines[-1].strip().endswith('right_arm"'):
                    lines[-1] = re.sub(r'right_arm"', 'slim_right"', lines[-1])
                elif lines[-1].strip().endswith('left_arm"'):
                    lines[-1] = re.sub(r'left_arm"', 'slim_left"', lines[-1])
            
            # Write the modified lines back to the file
            with open(file_path, 'w') as file:
                file.writelines(lines)

    # Create slim summon command
    summon_path = os.path.join(".", "data", "animated_java", "function", project, "summon")

    content = f"""# This file was generated by Animated Java via MC-Build. It is not recommended to edit this file directly.
function animated_java:{project}/summon {{args:{{variant: 'slim'}}}}"""
    
    file_path = os.path.join(summon_path, "slim.mcfunction")

    with open(file_path, "w") as file:
        file.write(content)
    
    print("Generated Slim variant")

def main():
    project, playerName, offsets = parse_arguments()

    print(f"Running aj-convert on project {project}")

    summonPath = os.path.join(".", "data", "animated_java", "function", project, "summon.mcfunction")
    read_and_modify_summon_function(summonPath, project, offsets, playerName)

    mcfunction_paths = [
        os.path.join(".", "data", "animated_java", "function", project, "set_default_pose.mcfunction"),
        os.path.join(".", "data", "animated_java", "function", project, "apply_default_pose.mcfunction")
    ]
    process_pose_files(mcfunction_paths, project, offsets)

    animations_rootpath = os.path.join(".", "data", "animated_java", "function", project, "animations")
    modify_animation_frames(animations_rootpath, project, offsets)

    process_default_variant_mcfunction(project,offsets)

    generate_slim_variant(project)

if __name__ == "__main__":
    main()

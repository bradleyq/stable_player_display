import sys
import nbtlib
import os

# Offset mappings for different player model modes
DEFAULT_OFFSETS = {
    "head": 0.0, "right_arm": -1024.0, "left_arm": -2048.0,
    "torso": -3072.0, "right_leg": -4096.0, "left_leg": -5120.0
}

SPLIT_OFFSETS = {
    "head": 0.0, "right_arm": -1024.0, "right_forearm": -6144.0,
    "left_arm": -2048.0, "left_forearm": -7168.0, "torso": -3072.0,
    "waist": -8192.0, "right_leg": -4096.0, "lower_right_leg": -9216.0,
    "left_leg": -5120.0, "lower_left_leg": -10240.0
}

def parse_cli_arguments():
    """Parse and validate command-line arguments."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    project = sys.argv[1]
    player_name = ""
    offsets = DEFAULT_OFFSETS

    for arg in sys.argv[2:]:
        if arg.startswith("-pn="):
            player_name = arg[4:]
        elif arg == "-split":
            offsets = SPLIT_OFFSETS

    return project, player_name, offsets

def print_usage():
    """Display usage instructions."""
    print("Usage: aj-convert.py [project] [optional:flags]")
    print("Available flags:")
    print("\t-pn=[playerName]\tSpecify the player skin (default: none)")
    print("\t-split\tEnable split mode with extra joints")

def modify_summon_file(filepath, project, offsets, player_name):
    """Modify the summon.mcfunction file with new offsets and player skin."""
    try:
        with open(filepath, "r") as file:
            summon_content = [file.readline() for _ in range(3)]
            summon_data = file.readline()

            if summon_data[-4] == ",":
                summon_data = summon_data[:-4] + summon_data[-3:]

            nbt_start = summon_data.index("~ ~ ~ ") + len("~ ~ ~ ")
            summon_content.append(summon_data[:nbt_start])
            nbt_data = summon_data[nbt_start:]

            nbt_root = nbtlib.parse_nbt(nbt_data)
            update_nbt_passengers(nbt_root, project, offsets, player_name)

            summon_content.append(nbtlib.serialize_tag(nbt_root, compact=True) + "\n")
            summon_content.append(file.readline())

        with open(filepath, "w") as file:
            file.writelines(summon_content)

        print(f"Successfully updated: {filepath}")

    except Exception as e:
        print(f"Error updating {filepath}: {e}")
        sys.exit(1)

def update_nbt_passengers(nbt_root, project, offsets, player_name):
    """Apply offsets and player skin to NBT passenger data."""
    for passenger in nbt_root["Passengers"][1:]:
        for bone_name, offset in offsets.items():
            tag = f"aj.{project}.bone.{bone_name}"
            if tag in passenger["Tags"]:
                passenger["transformation"]["translation"][1] += offset
                passenger["item_display"] = nbtlib.tag.String("thirdperson_righthand")
                passenger["item"]["id"] = nbtlib.tag.String("minecraft:player_head" if player_name else "minecraft:air")
                if player_name:
                    passenger["item"]["components"]["profile"] = nbtlib.tag.Compound({"name": nbtlib.tag.String(player_name)})

def update_pose_files(filepaths, project, offsets):
    """Update set_default_pose.mcfunction and apply_default_pose.mcfunction files."""
    for path in filepaths:
        try:
            with open(path, "r") as file:
                lines = [modify_pose_line(line, project, offsets) for line in file]

            with open(path, "w") as file:
                file.writelines(lines)

            print(f"Updated pose file: {path}")

        except Exception as e:
            print(f"Error processing {path}: {e}")
            sys.exit(1)

def modify_pose_line(line, project, offsets):
    """Modify a line with the appropriate transformation offset."""
    for bone_name, offset in offsets.items():
        tag = f"[tag=aj.{project}.bone.{bone_name}]"
        if tag in line:
            nbt_start = line.index("merge entity @s ") + len("merge entity @s ")
            tmp_line = line[:nbt_start]
            nbt_root = nbtlib.parse_nbt(line[nbt_start:])
            nbt_root["transformation"][7] += offset
            return tmp_line + nbtlib.serialize_tag(nbt_root, compact=True) + "\n"
    return line

def process_animation_frames(rootpath, offsets):
    """Modify all animation frames within the specified root directory."""
    try:
        for animation in os.listdir(rootpath):
            frames_path = os.path.join(rootpath, animation, "zzz", "frames")
            if not os.path.isdir(frames_path):
                continue

            frames = os.listdir(frames_path)
            for index, frame in enumerate(frames, start=1):
                frame_path = os.path.join(frames_path, frame)
                modify_frame_file(frame_path, offsets)
                sys.stdout.write(f"\rProcessing {animation} frames: [{index}/{len(frames)}]")
            print()

    except Exception as e:
        print(f"Error processing animation frames: {e}")
        sys.exit(1)

def modify_frame_file(filepath, offsets):
    """Modify an individual frame file by applying offsets."""
    try:
        with open(filepath, "r") as file:
            lines = [modify_frame_line(line, offsets) for line in file]

        with open(filepath, "w") as file:
            file.writelines(lines)

    except Exception as e:
        print(f"Error processing frame {filepath}: {e}")

def modify_frame_line(line, offsets):
    """Modify a frame line by adjusting transformation values."""
    for bone_name, offset in offsets.items():
        target = f"$data merge entity $(bone_{bone_name})"
        if target in line:
            nbt_start = line.index(") ") + len(") ")
            tmp_line = line[:nbt_start]
            nbt_root = nbtlib.parse_nbt(line[nbt_start:])
            nbt_root["transformation"][7] += offset
            return tmp_line + nbtlib.serialize_tag(nbt_root, compact=True) + "\n"
    return line

def main():
    project, player_name, offsets = parse_cli_arguments()

    print(f"Starting aj-convert for project: {project}")

    summon_filepath = os.path.join(".", "data", "animated_java", "function", project, "summon.mcfunction")
    modify_summon_file(summon_filepath, project, offsets, player_name)

    pose_filepaths = [
        os.path.join(".", "data", "animated_java", "function", project, "set_default_pose.mcfunction"),
        os.path.join(".", "data", "animated_java", "function", project, "apply_default_pose.mcfunction")
    ]
    update_pose_files(pose_filepaths, project, offsets)

    animation_rootpath = os.path.join(".", "data", "animated_java", "function", project, "animations")
    process_animation_frames(animation_rootpath, offsets)

if __name__ == "__main__":
    main()

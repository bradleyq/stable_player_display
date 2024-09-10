# Stable Player Display

This repository contains models and shaders to display any player skin using only a resource pack and display entities.

**The original repository is [here](https://github.com/bradleyq/stable_player_display/tree/main). This fork is intended to update the original work as long as I'm capable of doing so, and to provide better compatibility with [Animated Java](https://animated-java.dev/).**

## Limitations

- Use only with `item_display`.
- Do not modify `Rotation[1]` NBT (pitch).
- The model cannot be loaded from more than 512 meters **vertical distance** from the player (unlimited horizontal range).
- If using `transformation.translation[1]` for animations, subtract the required y-offset (if you are using AJ, the script handles this).

## Raw Item Displays

If you want to summon item displays, use the following commands (it is recommended to use a function):

```
summon minecraft:item_display ~ ~1.4 ~ {Tags:["head"],item_display:"thirdperson_righthand",view_range:0.6f,transformation:{translation:[0.0f,0.0f,0.0f],left_rotation:[0.0f,0.0f,0.0f,1.0f],scale:[1.0f,1.0f,1.0f],right_rotation:[0.0f,0.0f,0.0f,1.0f]}}
summon minecraft:item_display ~ ~1.4 ~ {Tags:["arm_r"],item_display:"thirdperson_righthand",view_range:0.6f,transformation:{translation:[0.0f,-1024.0f,0.0f],left_rotation:[0.0f,0.0f,0.0f,1.0f],scale:[1.0f,1.0f,1.0f],right_rotation:[0.0f,0.0f,0.0f,1.0f]}}
summon minecraft:item_display ~ ~1.4 ~ {Tags:["arm_l"],item_display:"thirdperson_righthand",view_range:0.6f,transformation:{translation:[0.0f,-2048.0f,0.0f],left_rotation:[0.0f,0.0f,0.0f,1.0f],scale:[1.0f,1.0f,1.0f],right_rotation:[0.0f,0.0f,0.0f,1.0f]}}
summon minecraft:item_display ~ ~1.4 ~ {Tags:["torso"],item_display:"thirdperson_righthand",view_range:0.6f,transformation:{translation:[0.0f,-3072.0f,0.0f],left_rotation:[0.0f,0.0f,0.0f,1.0f],scale:[1.0f,1.0f,1.0f],right_rotation:[0.0f,0.0f,0.0f,1.0f]}}
summon minecraft:item_display ~ ~0.7 ~ {Tags:["leg_r"],item_display:"thirdperson_righthand",view_range:0.6f,transformation:{translation:[0.0f,-4096.0f,0.0f],left_rotation:[0.0f,0.0f,0.0f,1.0f],scale:[1.0f,1.0f,1.0f],right_rotation:[0.0f,0.0f,0.0f,1.0f]}}
summon minecraft:item_display ~ ~0.7 ~ {Tags:["leg_l"],item_display:"thirdperson_righthand",view_range:0.6f,transformation:{translation:[0.0f,-5120.0f,0.0f],left_rotation:[0.0f,0.0f,0.0f,1.0f],scale:[1.0f,1.0f,1.0f],right_rotation:[0.0f,0.0f,0.0f,1.0f]}}
```

## Steps to Use

1. Export the player rig from Animated Java (AJ).
2. Modify the JSON file using the following script. Copy it to the AJ project folder:
```bash
python aj-convert.py
```

3. Run `aj-convert.py` in the datapack root folder:
   - **Run this script only once per AJ export!**
   - Requires `python3`.
   - Requires `nbtlib`: [https://pypi.org/project/nbtlib/](https://pypi.org/project/nbtlib/).
   - Usage: `aj-convert.py [project] [optional:flags]`.

Available flags:
- `-ns=[namespace]` : Internal project namespace. Default is `'zzzzzzzz'`.
- `-pn=[playerName]` : Player skin to use. Default is `''` (no skin), must be set later in-game.
- `-s` : Enable slim model. Default is disabled.

4. Delete the AJ resource pack if no other assets are needed (AJ-generated player assets are not required, as Stable Player Display will be used instead).
5. Summon the rig following the [AJ Documentation](https://animated-java.dev/docs/introduction/what-is-animated-java).
6. Use the provided loot tables (a slim variant is available) to update the AJ model in-game:

```
/loot replace entity @e[tag=aj.player_anim.bone.head] hotbar.0 loot player_anim:player/head
/loot replace entity @e[tag=aj.player_anim.bone.right_arm] hotbar.0 loot player_anim:player/right_arm
/loot replace entity @e[tag=aj.player_anim.bone.left_arm] hotbar.0 loot player_anim:player/left_arm
/loot replace entity @e[tag=aj.player_anim.bone.torso] hotbar.0 loot player_anim:player/torso
/loot replace entity @e[tag=aj.player_anim.bone.right_leg] hotbar.0 loot player_anim:player/right_leg
/loot replace entity @e[tag=aj.player_anim.bone.left_leg] hotbar.0 loot player_anim:player/left_leg
```

![You can also follow this video where I demonstrate all the steps](resources/2024-08-17_16-40-08.mp4).

### Variants

To use variants, extract the required files from the generated resource pack and merge them with the Stable Player Display resource pack. Ensure that you remove the "default" variant files; otherwise, the model parts will be overwritten.

## Issues You Might Encounter

- **When running the script**: The script includes multiple error checks for possible issues during processing. Please **READ** the messages output by the terminal carefully. I won't provide any help if the error is something like: `FileNotFoundError: [Errno 2] No such file or directory:` or similar. Make sure you are using the script correctly and in the proper directories. (However, if it worked in a previous AJ version but doesn't now, feel free to ask me.)

- **Problems with the resource pack**: The resource pack may break with each new version of Minecraft since shaders are still quite experimental. I'll try to update it to the latest version when possible. Make sure to use this repo with the last-supported Minecraft version, and wait for an update if a new version of Minecraft or Animated Java is released.

- **Editing the pivot points of the model**: If you've tried animating the AJ model, you may have found the pivot points inconvenient to work with and attempted to change them, which may have caused the model to distort. To fix this, you need to manually adjust the `translation` for each model part in `assets\minecraft\models\custom\entities\player`.

Make sure you have all the necessary libraries installed, export the project correctly, use ONLY the resource pack from this repo, test everything twice, and follow the AJ documentation. 

Please note, **I can't provide any help beyond updating the script and the shader**. If you want to add any other functionality, you will need to do it yourself.

If you encounter any errors or a new version breaks some aspect of the resource pack or script, feel free to DM me on Discord: **erkko_68**.

## Credits

- **Resonance#3633**: Providing custom models and base templates.
- **[sireroo](https://github.com/sireroo)**: Mild inspiration.
- **[bradleyq](https://github.com/bradleyq/stable_player_display/tree/main)**: Original creator.
---
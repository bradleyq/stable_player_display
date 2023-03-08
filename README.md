# Stable Player Display
models + shaders to display player models using new item_display entites. 

**This shader is stable on death, relog, unload, etc. The shader is not spawn order dependent.**

## caveats
- use on item_display only
- limited support for translucent skins (will dither instead)
- do not modify Rotation[1]
- model can not be loaded >512 meters **vertical distance** from player (unlimited horizontal range)
- if using transformation.transtation[1] for animations, subtract required y offset

## usage

```
/summon minecraft:item_display ~ ~1.4 ~ {Tags:["head"],item_display:"thirdperson_righthand",view_range:0.6f,transformation:{translation:[0.0f,0.0f,0.0f],left_rotation:[0.0f,0.0f,0.0f,1.0f],scale:[1.0f,1.0f,1.0f],right_rotation:[0.0f,0.0f,0.0f,1.0f]}}
/summon minecraft:item_display ~ ~1.4 ~ {Tags:["arm_r"],item_display:"thirdperson_righthand",view_range:0.6f,transformation:{translation:[0.0f,-1024.0f,0.0f],left_rotation:[0.0f,0.0f,0.0f,1.0f],scale:[1.0f,1.0f,1.0f],right_rotation:[0.0f,0.0f,0.0f,1.0f]}}
/summon minecraft:item_display ~ ~1.4 ~ {Tags:["arm_l"],item_display:"thirdperson_righthand",view_range:0.6f,transformation:{translation:[0.0f,-2048.0f,0.0f],left_rotation:[0.0f,0.0f,0.0f,1.0f],scale:[1.0f,1.0f,1.0f],right_rotation:[0.0f,0.0f,0.0f,1.0f]}}
/summon minecraft:item_display ~ ~1.4 ~ {Tags:["torso"],item_display:"thirdperson_righthand",view_range:0.6f,transformation:{translation:[0.0f,-3072.0f,0.0f],left_rotation:[0.0f,0.0f,0.0f,1.0f],scale:[1.0f,1.0f,1.0f],right_rotation:[0.0f,0.0f,0.0f,1.0f]}}
/summon minecraft:item_display ~ ~0.7 ~ {Tags:["leg_r"],item_display:"thirdperson_righthand",view_range:0.6f,transformation:{translation:[0.0f,-4096.0f,0.0f],left_rotation:[0.0f,0.0f,0.0f,1.0f],scale:[1.0f,1.0f,1.0f],right_rotation:[0.0f,0.0f,0.0f,1.0f]}}
/summon minecraft:item_display ~ ~0.7 ~ {Tags:["leg_l"],item_display:"thirdperson_righthand",view_range:0.6f,transformation:{translation:[0.0f,-5120.0f,0.0f],left_rotation:[0.0f,0.0f,0.0f,1.0f],scale:[1.0f,1.0f,1.0f],right_rotation:[0.0f,0.0f,0.0f,1.0f]}}
/item replace entity @e[tag=head] hotbar.0 with minecraft:player_head{SkullOwner:"Notch",CustomModelData:1}
/item replace entity @e[tag=arm_r] hotbar.0 with minecraft:player_head{SkullOwner:"Notch",CustomModelData:2}
/item replace entity @e[tag=arm_l] hotbar.0 with minecraft:player_head{SkullOwner:"Notch",CustomModelData:3}
/item replace entity @e[tag=torso] hotbar.0 with minecraft:player_head{SkullOwner:"Notch",CustomModelData:4}
/item replace entity @e[tag=leg_r] hotbar.0 with minecraft:player_head{SkullOwner:"Notch",CustomModelData:5}
/item replace entity @e[tag=leg_l] hotbar.0 with minecraft:player_head{SkullOwner:"Notch",CustomModelData:6}
```

- `view_range:0.6f` guarantees the player model will be unloaded within 512 blocks vertically
- `translation:` skin is loaded based on y offset:

  0 = head

  -1024 = right arm
  
  -2048 = left arm
  
  -3072 = torso
  
  -4096 = right leg
  
  -5120 = left leg
  
- `~ ~1.4 ~ ` when standing, head arms and torso pivot from here
- `~ ~0.7 ~`  when standing, legs pivot from here
- `SkullOwner:` player skin to load
- `CustomModelData:` each body part has its own custom model:

  1 = head
  
  2 = right arm
  
  3 = left arm
  
  4 = torso
  
  5 = right leg
  
  6 = left leg

## how it works

This shader makes use of item_displays not culling when out of player view. The translation can be set to a high value `n, 2n, 3n ...` to signal the shader. As long as the player is within `n/2` vertical distance of the model, the shader will be able to correctly identify the intended texture UVs to load.
  
## credits

**Resonance#3633** - providing custom models and base template
**https://github.com/sireroo** - mild inspiration

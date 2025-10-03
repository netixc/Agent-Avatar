# Live2D Model Reference Guide

This document provides detailed information about all available Live2D models including their expressions, motions, and interactive hit areas.

## Table of Contents
- [Asuna (16 Outfits)](#asuna-16-outfits)
- [Liko (10 Outfits)](#liko-10-outfits)
- [Haru (1 Outfit)](#haru-1-outfit)
- [Shizuku](#shizuku)
- [Epsilon](#epsilon)
- [Kato Megumi](#kato-megumi)
- [Tsukimi](#tsukimi)
- [Mao Pro (SDK 3)](#mao-pro-sdk-3)
- [Natori (SDK 3)](#natori-sdk-3)
- [RAYNOS-chan (SDK 3)](#raynos-chan-sdk-3)
- [Other Characters](#other-characters)

---

## Asuna (16 Outfits)

**Available Outfits:** 13, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29, 30, 33, 34, 35, 46

### Expressions (10 total)
- `F_FUN` - Happy/Fun
- `F_FUN_HANIKAMI` - Shy/Embarrassed smile
- `F_FUN_MAX` - Maximum happiness
- `F_FUN_SMILE` - Gentle smile
- `F_FUN_WARM` - Warm smile
- `F_NOMAL` - Normal/Neutral
- `F_SAD` - Sad
- `F_SURPRISE` - Surprised
- `F_ANGRY` - Angry
- `F_SLEEP` - Sleeping

### Motions
**Idle Motions (3):**
- IDLING
- IDLING_02
- IDLING_03

**Action Motions (16+):**
- I_ANGRY - Angry reaction
- I_ANGRY_S - Short angry
- I_ANGRY_W - Long angry
- I_FUN - Fun reaction
- I_FUN_S - Short fun
- I_FUN_W - Long fun
- I_SAD - Sad reaction
- I_SAD_S - Short sad
- I_SAD_W - Long sad
- I_SURPRISE - Surprised reaction
- I_SURPRISE_S - Short surprise
- I_SURPRISE_W - Long surprise
- I_SNEESE - Sneeze (outfits 19-30)
- REPEAT_01/02/03 - Repeating motions
- BYEBYE - Goodbye wave

### Interactive Hit Areas
- **Head** - Tap for head interactions
- **Chest** - Tap for chest reactions
- **Body** - Tap for body interactions

### SDK Version
Live2D Cubism SDK 2

---

## Liko (10 Outfits)

**Available Outfits:** 01, 02, 03, 04, 07, 09, 10, 12, 14, 15

### Expressions (10 total)
Same as Asuna:
- `F_FUN`, `F_FUN_HANIKAMI`, `F_FUN_MAX`, `F_FUN_SMILE`, `F_FUN_WARM`
- `F_NOMAL`, `F_SAD`, `F_SURPRISE`, `F_ANGRY`, `F_SLEEP`

### Motions
**Idle Motions (3):**
- idle/0.mtn
- idle/1.mtn
- idle/2.mtn

**Action Motions (19):**
- I_ANGRY, I_ANGRY_S, I_ANGRY_W
- I_FUN, I_FUN_S, I_FUN_W
- I_SAD, I_SAD_S, I_SAD_W
- I_SURPRISE, I_SURPRISE_S, I_SURPRISE_W
- IDLING, IDLING_02, IDLING_03
- REPEAT_01, REPEAT_02, REPEAT_03
- BYEBYE

### Interactive Hit Areas
- **Head** - Tap for head interactions
- **Chest** - Tap for chest reactions
- **Body** - Tap for body interactions
- **Foot** - Tap for foot reactions

### SDK Version
Live2D Cubism SDK 2

---

## Haru (1 Outfit)

**Available Outfit:** 02

### Expressions (5 total)
- `f01` - Neutral
- `f05` - Expression variant 1
- `f06` - Expression variant 2
- `f07` - Expression variant 3
- `f08` - Expression variant 4

### Motions
**Idle Motions (2):**
- idle_01.mtn
- idle_02.mtn

**Tap Body Motions (5):**
- tapBody_05 through tapBody_09

### Interactive Hit Areas
- **Head** - Tap for head interactions
- **Body** - Tap for body interactions

### SDK Version
Live2D Cubism SDK 2

---

## Shizuku

### Expressions (4 total)
- `f01` - Expression 1
- `f02` - Expression 2
- `f03` - Expression 3
- `f04` - Expression 4

### Motions
**Idle Motions (3):**
- idle_00, idle_01, idle_02

**Interactive Motions:**
- **Tap Body (3):** tapBody_00, tapBody_01, tapBody_02
- **Pinch In (3):** pinchIn_00, pinchIn_01, pinchIn_02
- **Pinch Out (3):** pinchOut_00, pinchOut_01, pinchOut_02
- **Shake (3):** shake_00, shake_01, shake_02
- **Flick Head (3):** flickHead_00, flickHead_01, flickHead_02

### Interactive Hit Areas
- **Head** - Tap or flick for head reactions
- **Mouth** - Tap for mouth interactions
- **Body** - Tap for body interactions

### Special Features
- Supports physics simulation
- Supports pose system
- Rich gesture-based interactions (pinch, shake, flick)

### SDK Version
Live2D Cubism SDK 2

---

## Epsilon

### Expressions (8 total)
- `f01` through `f08` - 8 expression variants

### Motions
**Idle Motion (1):**
- Epsilon2.1_idle_01.mtn

**Action Motions (14):**
- Epsilon2.1_m_01 through m_08 - Main motions
- Epsilon2.1_m_sp_01 through sp_05 - Special motions
- Epsilon2.1_shake_01 - Shake motion

### SDK Version
Live2D Cubism SDK 2

---

## Kato Megumi

### Expressions (6 total)
6 unique facial expressions mapped to emotions

### Motions
Includes idle and interaction motions

### Interactive Hit Areas
- **Head** - Tap for head interactions

### SDK Version
Live2D Cubism SDK 2

---

## Tsukimi

### Expressions (10 total)
10 facial expressions mapped to various emotions

### Motions
Includes idle and action motion sequences

### SDK Version
Live2D Cubism SDK 2

---

## Mao Pro (SDK 3)

### Expressions (8 total)
- `exp_01` through `exp_08` - 8 expression variants

### Motions
**Idle Motion (1):**
- mtn_01.motion3.json

**Action Motions (6):**
- mtn_02, mtn_03, mtn_04 - Main motions
- special_01, special_02, special_03 - Special motions

### Interactive Hit Areas
- **HitAreaHead** - Head interactions
- **HitAreaBody** - Body interactions

### Special Features
- Advanced eye blink system
- Lip sync support
- Enhanced physics simulation

### SDK Version
Live2D Cubism SDK 3

---

## Natori (SDK 3)

### Expressions (11 total)
Named expressions with clear emotion mapping:
- `Angry` - Angry expression
- `Blushing` - Blushing/Embarrassed
- `Normal` - Neutral/Default
- `Sad` - Sad expression
- `Smile` - Happy/Smiling
- `Surprised` - Surprised expression
- `exp_01` through `exp_05` - Additional expression variants

### Motions
**Idle Motions (3):**
- mtn_00.motion3.json
- mtn_01.motion3.json
- mtn_02.motion3.json

**TapBody Motions (5):**
- mtn_03.motion3.json
- mtn_04.motion3.json
- mtn_05.motion3.json
- mtn_06.motion3.json
- mtn_07.motion3.json

### Interactive Hit Areas
- **HitAreaHead** - Head interactions
- **HitAreaBody** - Body interactions

### Special Features
- Named emotion expressions for easy mapping
- Most expressions of any SDK 3 model (11 total)
- Physics simulation
- Multiple tap body reactions

### SDK Version
Live2D Cubism SDK 3

---

## RAYNOS-chan (SDK 3)

### Expressions (8 total)
- `expression0` - Neutral/Default
- `expression1` - Happy/Joy
- `expression2` - Sad
- `expression3` - Angry
- `expression4` - Surprised
- `expression5` - Fearful
- `expression6` - Disgusted
- `expression7` - Smirk/Playful

### Motions
No pre-defined motion groups (VTube Studio handles motions)

### Interactive Hit Areas
No configured hit areas (VTube Studio handles interactions)

### Special Features
- **VTube Studio optimized** - Designed specifically for VTubing
- Physics simulation with advanced hair/clothing dynamics
- Full emotion set with all 8 basic expressions
- High-quality 2K textures
- Perfect compatibility (moc3 version 5)

### SDK Version
Live2D Cubism SDK 3 (moc3 version 5)

---

## Other Characters

The following characters are also available with similar feature sets:

- **Erika** - 1 model
- **Mirai** - 1 model
- **Murakumo** - 1 model
- **Wanko** - 1 model
- **Yukari** - 1 model

Each includes expressions, idle motions, and interactive hit areas suitable for AI avatar interactions.

---

## Emotion Mapping

The system automatically maps AI emotions to Live2D expressions:

| AI Emotion | Asuna/Liko | Shizuku | Haru | Mao Pro |
|------------|------------|---------|------|---------|
| neutral | F_NOMAL (3) | f01 (0) | f01 (0) | exp_01 (0) |
| joy | F_FUN (0) | f04 (3) | f05 (1) | exp_04 (3) |
| sadness | F_SAD (4) | f02 (1) | f06 (2) | exp_02 (1) |
| anger | F_ANGRY (7) | f03 (2) | f07 (3) | exp_03 (2) |
| surprise | F_SURPRISE (6) | f02 (1) | f07 (3) | exp_04 (3) |
| fear | F_SAD (4) | f04 (3) | f06 (2) | exp_02 (1) |
| disgust | F_ANGRY (7) | f03 (2) | f07 (3) | exp_03 (2) |
| smirk | F_FUN_SMILE (1) | f04 (3) | f05 (1) | exp_04 (3) |

---

## Usage Notes

### Model Selection
All models can be selected through the web interface at `http://localhost:12393`. Character presets are automatically loaded from the `characters/` directory.

### Performance
- SDK 2 models are lighter and recommended for most systems
- SDK 3 models (Mao Pro) offer enhanced features but require more resources

### Customization
To create custom character presets:
1. Copy an existing YAML file from `characters/`
2. Modify the `live2d_model_name` to match your chosen model
3. Adjust emotion mappings if needed
4. Save with a descriptive filename

### Physics and Pose
Models with physics support will respond naturally to motion and interactions. The pose system ensures smooth transitions between different states.

---

## Technical Details

### File Structure
```
assets/live2d-models/
├── asuna/          # 16 outfit folders (13, 19-30, 33-35, 46)
├── liko/           # 10 outfit folders (01-04, 07, 09-10, 12, 14-15)
├── haru/           # 1 outfit folder (02)
├── shizuku/        # Single model
├── epsilon/        # Single model
├── kato/           # Single model
├── tsukimi/        # Single model
├── mao_pro/        # SDK 3 model
└── [others]/       # Additional characters
```

### Configuration Files
- `.model.json` / `.model3.json` - Main model definition
- `.physics.json` / `.physics3.json` - Physics simulation
- `.pose.json` / `.pose3.json` - Pose system
- `.exp.json` / `.exp3.json` - Expression data
- `.mtn` / `.motion3.json` - Motion data

---

## Credits

Live2D models are third-party assets. Please respect the original creators' licenses and terms of use.

For more information about Live2D Cubism, visit: https://www.live2d.com/

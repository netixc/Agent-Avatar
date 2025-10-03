# Emotion Mapping Guide for Live2D Models

This guide explains how to configure emotion mappings for Live2D models in Agent-Avatar.

## Understanding Emotion Mapping

The `emotionMap` in `model_dict.json` maps AI emotion tags (like `[joy]`, `[sadness]`) to Live2D expression indices. When Agent-Zero responds with emotion tags, the system uses this mapping to display the correct facial expression.

## Step-by-Step Configuration

### Step 1: Identify Expression Order

First, check your model's JSON file to see what expressions exist and their order:

```bash
cat assets/live2d-models/YOUR_MODEL/model.json | python3 -m json.tool | grep -A 20 "expressions"
```

**Example output for Haru:**
```json
"expressions": [
    {"name": "f01", "file": "common/expressions/f01.exp.json"},  // Index 0
    {"name": "f05", "file": "common/expressions/f05.exp.json"},  // Index 1
    {"name": "f06", "file": "common/expressions/f06.exp.json"},  // Index 2
    {"name": "f07", "file": "common/expressions/f07.exp.json"},  // Index 3
    {"name": "f08", "file": "common/expressions/f08.exp.json"}   // Index 4
]
```

### Step 2: Understand What Each Expression Represents

Look at the expression files to understand what emotion each represents. For Haru:

- **Index 0 (f01)**: Neutral - empty expression, default face
- **Index 1 (f05)**: Happy - closed smiling eyes, raised eyebrows
- **Index 2 (f06)**: Surprised - wide open eyes, open mouth
- **Index 3 (f07)**: Shy/Embarrassed - smile with blush (TERE parameter)
- **Index 4 (f08)**: Sad - sad eyes and mouth

**Quick check command:**
```bash
# See what parameters each expression modifies
cat assets/live2d-models/haru/common/expressions/f05.exp.json
```

### Step 3: Create the Emotion Map

In `model_dict.json`, map AI emotions to expression indices:

```json
{
  "name": "haru_02",
  "emotionMap": {
    "neutral": 0,    // f01 - neutral face
    "joy": 1,        // f05 - happy smile
    "surprise": 2,   // f06 - surprised face
    "smirk": 3,      // f07 - shy smile with blush
    "sadness": 4,    // f08 - sad face
    "anger": 4,      // Reuse sad for anger (or create new)
    "fear": 4,       // Reuse sad for fear
    "disgust": 4     // Reuse sad for disgust
  }
}
```

### Available AI Emotions

The system recognizes these emotion tags:
- `neutral` - Default, calm
- `joy` - Happy, cheerful
- `sadness` - Sad, disappointed
- `anger` - Angry, frustrated
- `surprise` - Surprised, shocked
- `fear` - Scared, worried
- `disgust` - Disgusted, uncomfortable
- `smirk` - Smug, thinking, playful

### Step 4: Test the Configuration

**Method 1: Browser Console Expression Tester (Recommended)**

For quick, direct testing without Agent-Zero interaction:

1. Open Agent-Avatar in your browser (http://localhost:12393)
2. Open browser console (F12 or Right-click → Inspect → Console)
3. Copy and paste the contents of `tests/expression-test-universal.js` into the console
4. A test panel will appear - click buttons to test each expression index
5. Note which expression corresponds to each emotion for your emotionMap

**Method 2: Agent-Zero Chat Testing**

1. Save your changes to `model_dict.json`
2. Restart the Docker container:
   ```bash
   docker restart vtube
   ```
3. Test each emotion by asking Agent-Zero to use emotion tags:
   ```
   User: "show a happy face"
   User: "show a sad face"
   User: "show surprise"
   ```

### Step 5: Monitor Logs

Check if emotions are being extracted correctly:

```bash
docker logs vtube --tail 100 | grep "Extracted expressions"
```

**Expected output:**
```
Extracted expressions [1] from text: [joy] Here's a smile for you!
Extracted expressions [4] from text: [sadness] Here's a sad face for you.
```

The number in brackets `[1]` should match your emotionMap index!

## Common Model Types

### SDK 2 Models (Most Common)

**File format:** `.model.json` or just `.json`

**Expression structure:**
```json
"expressions": [
    {"name": "f01", "file": "expressions/f01.exp.json"},
    {"name": "f02", "file": "expressions/f02.exp.json"}
]
```

**Examples:** Asuna, Liko, Haru, Shizuku, Epsilon

### SDK 3 Models (Newer)

**File format:** `.model3.json`

**Expression structure:**
```json
"Expressions": [
    {"Name": "exp_01", "File": "expressions/exp_01.exp3.json"},
    {"Name": "exp_02", "File": "expressions/exp_02.exp3.json"}
]
```

**Example:** Mao Pro

## Example Configurations

### Shizuku (4 expressions)

```json
"emotionMap": {
  "neutral": 0,    // f01 - neutral
  "sadness": 1,    // f02 - sad
  "anger": 2,      // f03 - angry
  "joy": 3,        // f04 - happy
  "surprise": 3,   // Reuse f04
  "fear": 1,       // Reuse f02 (sad)
  "disgust": 2,    // Reuse f03 (angry)
  "smirk": 3       // Reuse f04 (happy)
}
```

### Asuna/Liko (10 expressions)

```json
"emotionMap": {
  "neutral": 3,    // F_NOMAL
  "joy": 0,        // F_FUN
  "smirk": 1,      // F_FUN_HANIKAMI (shy smile)
  "sadness": 4,    // F_SAD
  "surprise": 6,   // F_SURPRISE
  "anger": 7,      // F_ANGRY
  "fear": 4,       // Reuse F_SAD
  "disgust": 7     // Reuse F_ANGRY
}
```

### Mao Pro SDK 3 (8 expressions)

```json
"emotionMap": {
  "neutral": 0,    // exp_01
  "sadness": 1,    // exp_02
  "anger": 2,      // exp_03
  "joy": 3,        // exp_04
  "surprise": 4,   // exp_05
  "fear": 5,       // exp_06
  "disgust": 6,    // exp_07
  "smirk": 7       // exp_08
}
```

## Troubleshooting

### Problem: Expressions don't change

**Check logs:**
```bash
docker logs vtube --tail 50 | grep -i "expression\|emotion"
```

**Possible causes:**
1. Wrong expression index in emotionMap
2. Expression files don't exist
3. Model not reloaded after config change

**Solution:**
- Verify expression order matches your emotionMap
- Restart Docker: `docker restart vtube`
- Check if expression files exist in model folder

### Problem: Wrong expression displayed

**Example:** Joy shows sad face

**Cause:** Incorrect index mapping

**Fix:**
1. Check actual expression order in model.json
2. Test each expression file to see what it does
3. Update emotionMap with correct indices

### Problem: Some emotions missing

If your model has fewer expressions than emotions, reuse similar expressions:

```json
"emotionMap": {
  "neutral": 0,
  "joy": 1,
  "surprise": 2,
  "smirk": 1,      // Reuse joy for smirk
  "sadness": 3,
  "anger": 3,      // Reuse sad for anger
  "fear": 3,       // Reuse sad for fear
  "disgust": 3     // Reuse sad for disgust
}
```

## Advanced: Creating Custom Expressions

If you want to add new expressions to an existing model:

1. Create a new `.exp.json` file in the expressions folder
2. Add it to the model's JSON file expressions array
3. Update emotionMap to use the new expression index

**Example expression file:**
```json
{
  "type": "Live2D Expression",
  "fade_in": 500,
  "fade_out": 500,
  "params": [
    {"id": "PARAM_EYE_L_OPEN", "val": 2, "calc": "mult"},
    {"id": "PARAM_EYE_R_OPEN", "val": 2, "calc": "mult"},
    {"id": "PARAM_MOUTH_FORM", "val": 1}
  ]
}
```

## Reference: Expression Parameters

Common parameters in Live2D expressions:

- `PARAM_EYE_L_OPEN` / `PARAM_EYE_R_OPEN` - Eye opening (0=closed, 1=open)
- `PARAM_EYE_L_SMILE` / `PARAM_EYE_R_SMILE` - Smiling eyes
- `PARAM_BROW_L_Y` / `PARAM_BROW_R_Y` - Eyebrow position
- `PARAM_BROW_L_FORM` / `PARAM_BROW_R_FORM` - Eyebrow shape
- `PARAM_MOUTH_FORM` - Mouth shape (-1=sad, 0=neutral, 1=smile)
- `PARAM_TERE` - Blush effect

## Quick Reference Commands

```bash
# Check expression order
cat assets/live2d-models/MODEL_NAME/model.json | python3 -m json.tool | grep -A 20 "expressions"

# View expression file contents
cat assets/live2d-models/MODEL_NAME/expressions/f01.exp.json

# Check emotion extraction in logs
docker logs vtube --tail 100 | grep "Extracted expressions"

# Restart after config changes
docker restart vtube

# Test specific emotion
# In chat: "show a happy face" or "show sadness"
```

## Summary

1. Find expression order in model.json
2. Understand what each expression represents
3. Map AI emotions to correct expression indices
4. Save to model_dict.json
5. Restart Docker
6. Test and verify in logs

The key is making sure the **index numbers** in your emotionMap match the **position** of expressions in the model's JSON file!

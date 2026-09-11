MIGRATE_GUIDE = """
================================================================
  jadidi engine: manual migration guide
================================================================

This guide helps you migrate an older project to the latest
engine version. Follow the steps below manually.

----------------------------------------------------------------
STEP 1: Build the latest engine
----------------------------------------------------------------

    jadidi-hub engine-sync
    jadidi-hub engine-build

----------------------------------------------------------------
STEP 2: Replace the engine binary
----------------------------------------------------------------

  Find the latest build:

    ls ~/.jadidi/builds/

  Copy it over the old binary in your project:

    cp ~/.jadidi/builds/<tag>/jadidi  <project>/jadidi

  On Windows, use jadidi.exe instead.

----------------------------------------------------------------
STEP 3: Update 'ide autocompletion'
----------------------------------------------------------------

  The engine ships Lua API definitions for your editor.
  Replace the old copy with the new one:

    rm -rf "<project>/ide autocompletion"
    cp -r ~/.jadidi/sources/jadidi/"ide autocompletion" \\
          "<project>/"

----------------------------------------------------------------
STEP 4: Update shaders (if you have not modified them)
----------------------------------------------------------------

  The sprite shaders changed. New uniforms were added:

    sprite.vert:
      + uniform vec2 uvOffset;
      + uniform vec2 uvScale;
      ~ TexCoord = aTexCoord * uvScale + uvOffset;

    sprite.frag:
      + uniform bool useTexture;
      ~ Branch on useTexture to support solid-color sprites.

  If you have NOT customized your shaders, overwrite them:

    cp <project>/Shaders/sprite.vert  <project>/Shaders/sprite.vert.bak
    cp <project>/Shaders/sprite.frag  <project>/Shaders/sprite.frag.bak

  Then regenerate them by creating a temporary project and copying
  the shaders, or write the new content manually.

  If you HAVE customized your shaders, merge the changes by hand.

----------------------------------------------------------------
STEP 5: Move schemas to .vscode (VSCode users)
----------------------------------------------------------------

  Older projects placed schemas at the project root:

    <project>/schemas/

  Newer projects place them inside .vscode:

    <project>/.vscode/schemas/

  Run the editor setup command to do this automatically:

    jadidi-hub setup-editor <project>

  This also creates .vscode/settings.json and .zed/settings.json
  with the correct schema references.

----------------------------------------------------------------
STEP 6: Fix breaking API changes in scene files
----------------------------------------------------------------

  Several component fields changed between versions.
  Update every Scenes/*.json file accordingly.

  6a. BoxCollider
      OLD:  "boxCollider": { "w": 32, "h": 32 }
      NEW:  "boxCollider": { "x": 32, "y": 32, "isTrigger": false }

      w  ->  x
      h  ->  y
      + isTrigger (boolean, optional, default false)

  6b. Rigidbody
      OLD:  "rigidbody": { "isDynamic": true, ... }
      NEW:  "rigidbody": { "bodyType": "dynamic", ... }

      isDynamic (bool)  ->  bodyType (string)
        true   ->  "dynamic"
        false  ->  "static"
      New option: "kinematic"

  6c. Transform
      A new optional field was added:

      "transform": {
          "position": { "x": 0, "y": 0 },
          "scale":    { "x": 1, "y": 1 },
          "rotation": 0.0
      }

      rotation is optional and defaults to 0.0.
      No action needed unless you want to use it.

----------------------------------------------------------------
STEP 7: Update animation files (optional)
----------------------------------------------------------------

  The loop field default changed.

  OLD default:  "loop": true
  NEW default:  "loop": false

  If your animations relied on the old default (loop = true
  when the field was missing), add "loop": true explicitly
  to every Animations/*.json file.

----------------------------------------------------------------
STEP 8: Verify
----------------------------------------------------------------

  Run the game and check the console for errors:

    cd <project>
    ./jadidi

  Watch for:
    - Unknown component names in scene files
    - Missing texture paths
    - Lua API errors in Scripts/

----------------------------------------------------------------
STEP 9: Update .gitignore (if the project is a git repo)
----------------------------------------------------------------

  Make sure the engine binary is ignored:

    echo "jadidi" >> <project>/.gitignore

  On Windows:

    echo "jadidi.exe" >> <project>/.gitignore

================================================================
  Quick command summary
================================================================

  jadidi-hub engine-sync
  jadidi-hub engine-build
  jadidi-hub setup-editor <project>

  Then manually:
    - Replace the binary
    - Update ide autocompletion
    - Fix scene JSON fields (x/y, bodyType, rotation)
    - Fix animation loop defaults
    - Update or merge shaders
"""


def show_migrate_guide():
    print(MIGRATE_GUIDE)
    return 0
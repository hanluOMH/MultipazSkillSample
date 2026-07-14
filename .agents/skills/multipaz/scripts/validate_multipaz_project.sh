#!/usr/bin/env bash

set -euo pipefail

DRY_RUN=0
PROJECT_PATH="."

usage() {
  cat <<'EOF'
Usage: validate_multipaz_project.sh [--dry-run] [project-path]

Runs non-destructive validation steps for a Multipaz-integrated project.
In dry-run mode the script still executes local inspection scripts but only prints
Gradle and Xcode validation commands.
EOF
}

run_or_print() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '[dry-run] %s\n' "$*"
  else
    printf '[run] %s\n' "$*"
    "$@"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      PROJECT_PATH="$1"
      shift
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="$(cd "$PROJECT_PATH" && pwd)"

if [[ ! -d "$PROJECT_PATH" ]]; then
  echo "error: invalid project path: $PROJECT_PATH" >&2
  exit 2
fi

if [[ ! -f "$PROJECT_PATH/settings.gradle.kts" ]]; then
  echo "error: settings.gradle.kts not found under $PROJECT_PATH" >&2
  exit 2
fi

echo "Inspecting project at $PROJECT_PATH"
python3 -B "$SCRIPT_DIR/inspect_multipaz_project.py" "$PROJECT_PATH" --summary-only
echo
python3 -B "$SCRIPT_DIR/check_multipaz_dependencies.py" "$PROJECT_PATH" >/dev/null
echo "Dependency inspection completed"

MODULES=()
while IFS= read -r module; do
  MODULES+=("$module")
done < <(python3 - <<'PY' "$PROJECT_PATH/settings.gradle.kts"
import re
import sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding="utf-8")
for match in re.findall(r'include\(":(.*?)"\)', text):
    print(match)
PY
)

HAS_GRADLEW=0
if [[ -x "$PROJECT_PATH/gradlew" ]]; then
  HAS_GRADLEW=1
fi

HAS_XCODEBUILD=0
if command -v xcodebuild >/dev/null 2>&1; then
  HAS_XCODEBUILD=1
fi

contains_module() {
  local needle="$1"
  for module in "${MODULES[@]}"; do
    if [[ "$module" == "$needle" ]]; then
      return 0
    fi
  done
  return 1
}

if [[ "$HAS_GRADLEW" -eq 0 ]]; then
  echo "warning: gradlew not found or not executable; skipping Gradle validation commands"
else
  run_or_print "$PROJECT_PATH/gradlew" -p "$PROJECT_PATH" help
  if contains_module "multipaz"; then
    run_or_print "$PROJECT_PATH/gradlew" -p "$PROJECT_PATH" :multipaz:assemble
    run_or_print "$PROJECT_PATH/gradlew" -p "$PROJECT_PATH" :multipaz:jvmTest
  fi
  if contains_module "samples:testapp"; then
    run_or_print "$PROJECT_PATH/gradlew" -p "$PROJECT_PATH" :samples:testapp:assembleDebug
  fi
  if contains_module "androidApp"; then
    run_or_print "$PROJECT_PATH/gradlew" -p "$PROJECT_PATH" :androidApp:assembleDebug
  fi
  if contains_module "shared"; then
    run_or_print "$PROJECT_PATH/gradlew" -p "$PROJECT_PATH" :shared:compileKotlinIosSimulatorArm64
  fi
  if contains_module "multipaz-compose"; then
    run_or_print "$PROJECT_PATH/gradlew" -p "$PROJECT_PATH" :multipaz-compose:assemble
  fi
fi

if contains_module "samples:testapp" && grep -Rqs "android.permission.NFC" "$PROJECT_PATH/samples/testapp/src/androidMain/AndroidManifest.xml"; then
  if [[ "$HAS_GRADLEW" -eq 1 ]]; then
    run_or_print "$PROJECT_PATH/gradlew" -p "$PROJECT_PATH" :samples:testapp:compileBlueDebugKotlinAndroid
  fi
  echo "note: Android NFC runtime validation still requires physical Android hardware."
fi

if contains_module "samples:SwiftTestApp"; then
  if [[ "$HAS_XCODEBUILD" -eq 1 ]]; then
    run_or_print xcodebuild -project "$PROJECT_PATH/samples/SwiftTestApp/SwiftTestApp.xcodeproj" -scheme SwiftTestApp -sdk iphonesimulator build
  else
    echo "note: xcodebuild is unavailable; skipping iOS compilation checks."
  fi
fi

echo "note: do not attempt to validate an iOS Multipaz NFC implementation because that workflow is currently unsupported."

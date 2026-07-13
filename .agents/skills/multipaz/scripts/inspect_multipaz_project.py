#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


TARGET_PATTERNS = {
    "android": re.compile(r"\bandroidTarget\s*\("),
    "jvm": re.compile(r"\bjvm\s*\("),
    "js": re.compile(r"\bjs\s*\("),
    "wasmJs": re.compile(r"\bwasmJs\s*\("),
    "iosX64": re.compile(r"\biosX64\s*\("),
    "iosArm64": re.compile(r"\biosArm64\s*\("),
    "iosSimulatorArm64": re.compile(r"\biosSimulatorArm64\s*\("),
    "cocoapods": re.compile(r"\bcocoapods\s*\("),
}

MULTIPAZ_DEP_RE = re.compile(
    r"""(?:
        project\(\s*":(?P<project>multipaz[^"]*)"\s*\) |
        ["'](?P<artifact>org\.multipaz:[^:"']+)(?::(?P<version>[^"']+))?["']
    )""",
    re.VERBOSE,
)
INCLUDE_RE = re.compile(r'include\(":(.*?)"\)')
WRAPPER_RE = re.compile(r"distributionUrl=.*gradle-([^-]+)-")
ANDROID_NAMESPACE_RE = re.compile(r'namespace\s*=\s*"([^"]+)"')
COMPILE_SDK_RE = re.compile(r"compileSdk\s*=\s*([^\n]+)")
JAVA_TARGET_RE = re.compile(r"JvmTarget\.([A-Z0-9_]+)")
ALIAS_VERSION_RE = re.compile(r'alias\(libs\.plugins\.([^)]+)\)')
SUSPICIOUS_IOS_NFC_RE = re.compile(r"CoreNFC|NFCNDEFReaderSession|NFCTagReaderSession|com\.apple\.developer\.nfc", re.I)


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def rel(path: Path, root: Path) -> str:
    return os.path.relpath(path, root)


def find_files(root: Path, *names: str) -> list[Path]:
    matched: list[Path] = []
    for name in names:
        matched.extend(path for path in root.rglob(name) if "build" not in path.parts)
    return sorted(set(matched))


def parse_versions(root: Path) -> dict:
    versions = {
        "gradle_wrapper": None,
        "kotlin": None,
        "agp": None,
        "compose": None,
        "android_compile_sdk": None,
    }
    wrapper = root / "gradle" / "wrapper" / "gradle-wrapper.properties"
    wrapper_text = read_text(wrapper)
    if wrapper_text:
        match = WRAPPER_RE.search(wrapper_text)
        if match:
            versions["gradle_wrapper"] = match.group(1)

    libs_toml = root / "gradle" / "libs.versions.toml"
    if tomllib and libs_toml.exists():
        data = tomllib.loads(libs_toml.read_text(encoding="utf-8"))
        version_table = data.get("versions", {})
        versions["kotlin"] = version_table.get("kotlin")
        versions["agp"] = version_table.get("agp")
        versions["compose"] = version_table.get("compose-plugin")
        versions["android_compile_sdk"] = version_table.get("android-compileSdk")
    return versions


def parse_modules(root: Path) -> list[str]:
    settings = read_text(root / "settings.gradle.kts") or ""
    return sorted(set(INCLUDE_RE.findall(settings)))


def collect_build_files(root: Path) -> list[Path]:
    return sorted(root.rglob("build.gradle.kts"))


def detect_targets(build_text: str) -> list[str]:
    found = [name for name, pattern in TARGET_PATTERNS.items() if pattern.search(build_text)]
    return sorted(found)


def scan_dependencies(text: str) -> list[dict]:
    deps = []
    for match in MULTIPAZ_DEP_RE.finditer(text):
        if match.group("project"):
            deps.append({"kind": "project", "value": match.group("project")})
        else:
            deps.append(
                {
                    "kind": "artifact",
                    "value": match.group("artifact"),
                    "version": match.group("version"),
                }
            )
    return deps


def scan_source_sets(root: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for src_dir in root.rglob("src"):
        children = [child.name for child in src_dir.iterdir() if child.is_dir()]
        if children:
            result[rel(src_dir.parent, root)] = sorted(children)
    return dict(sorted(result.items()))


def scan_manifests(root: Path) -> dict:
    manifests = [rel(path, root) for path in find_files(root, "AndroidManifest.xml")]
    plists = [rel(path, root) for path in root.rglob("*.plist")]
    entitlements = [rel(path, root) for path in root.rglob("*.entitlements")]

    android_nfc = []
    for manifest in find_files(root, "AndroidManifest.xml"):
        text = read_text(manifest) or ""
        if "android.hardware.nfc" in text or "android.permission.NFC" in text or "BIND_NFC_SERVICE" in text:
            android_nfc.append(
                {
                    "path": rel(manifest, root),
                    "uses_feature_nfc": "android.hardware.nfc" in text,
                    "uses_permission_nfc": "android.permission.NFC" in text,
                    "bind_nfc_service": "BIND_NFC_SERVICE" in text,
                }
            )

    suspicious_ios = []
    for path in [*root.rglob("*.swift"), *root.rglob("*.plist"), *root.rglob("*.entitlements"), *root.rglob("project.pbxproj")]:
        if "build" in path.parts:
            continue
        text = read_text(path)
        if text and SUSPICIOUS_IOS_NFC_RE.search(text):
            suspicious_ios.append(rel(path, root))

    return {
        "android_manifests": manifests,
        "ios_plists": plists,
        "ios_entitlements": entitlements,
        "android_nfc": android_nfc,
        "suspicious_ios_nfc_configuration": sorted(set(suspicious_ios)),
    }


def infer_roles(modules: list[str]) -> dict[str, list[str]]:
    roles = {"holder": [], "verifier": [], "issuer": [], "server": []}
    for module in modules:
        if "testapp" in module or "swifttestapp" in module.lower():
            roles["holder"].append(module)
        if "verifier" in module:
            roles["verifier"].append(module)
        if "openid4vci" in module or "backend" in module:
            roles["issuer"].append(module)
        if "server" in module or "deployment" in module:
            roles["server"].append(module)
    return roles


def build_report(root: Path) -> dict:
    build_files = collect_build_files(root)
    modules = parse_modules(root)
    target_info = {}
    dependencies = {}
    namespaces = {}
    compile_sdks = {}
    jvm_targets = {}
    compose_usage = []
    convention_plugins = set()
    cocoapods_modules = []

    for build_file in build_files:
        text = read_text(build_file) or ""
        key = rel(build_file, root)
        target_info[key] = detect_targets(text)
        dependencies[key] = scan_dependencies(text)

        namespace_match = ANDROID_NAMESPACE_RE.search(text)
        if namespace_match:
            namespaces[key] = namespace_match.group(1)
        compile_sdk_match = COMPILE_SDK_RE.search(text)
        if compile_sdk_match:
            compile_sdks[key] = compile_sdk_match.group(1).strip()
        jvm_targets[key] = sorted(set(JAVA_TARGET_RE.findall(text)))
        if "jetbrainsCompose" in text or "compose." in text:
            compose_usage.append(key)
        if "cocoapods" in target_info[key]:
            cocoapods_modules.append(key)
        for alias in ALIAS_VERSION_RE.findall(text):
            if alias.startswith("org.multipaz") or alias.startswith("skie"):
                convention_plugins.add(alias)

    report = {
        "project_root": str(root),
        "versions": parse_versions(root),
        "modules": modules,
        "build_files": [rel(path, root) for path in build_files],
        "targets_by_build_file": target_info,
        "source_sets": scan_source_sets(root),
        "dependencies": dependencies,
        "android_namespaces": namespaces,
        "android_compile_sdk_by_build_file": compile_sdks,
        "jvm_targets_by_build_file": jvm_targets,
        "compose_usage": sorted(set(compose_usage)),
        "version_catalogs": [rel(path, root) for path in find_files(root, "libs.versions.toml")],
        "included_builds": ["build-logic"] if (root / "build-logic").exists() else [],
        "convention_plugins": sorted(convention_plugins),
        "cocoapods_modules": sorted(set(cocoapods_modules)),
        "swift_package_present": (root / "Package.swift").exists(),
        "platform_files": scan_manifests(root),
        "likely_roles": infer_roles(modules),
        "warnings": [],
    }
    if not modules:
        report["warnings"].append("No Gradle modules detected from settings.gradle.kts")
    if report["versions"]["kotlin"] is None:
        report["warnings"].append("Could not determine Kotlin version from gradle/libs.versions.toml")
    return report


def print_summary(report: dict) -> None:
    print("Multipaz project inspection summary")
    print(f"Root: {report['project_root']}")
    versions = report["versions"]
    print(
        "Versions: "
        f"Gradle={versions['gradle_wrapper'] or 'unknown'}, "
        f"Kotlin={versions['kotlin'] or 'unknown'}, "
        f"AGP={versions['agp'] or 'unknown'}, "
        f"Compose={versions['compose'] or 'unknown'}, "
        f"compileSdk={versions['android_compile_sdk'] or 'unknown'}"
    )
    print(f"Modules ({len(report['modules'])}): {', '.join(report['modules'][:12])}" + (" ..." if len(report["modules"]) > 12 else ""))
    if report["compose_usage"]:
        print(f"Compose usage: {', '.join(report['compose_usage'][:6])}" + (" ..." if len(report["compose_usage"]) > 6 else ""))
    if report["platform_files"]["android_nfc"]:
        print("Android NFC manifests:")
        for item in report["platform_files"]["android_nfc"]:
            print(f"  - {item['path']}")
    if report["platform_files"]["suspicious_ios_nfc_configuration"]:
        print("iOS NFC-related configuration found:")
        for item in report["platform_files"]["suspicious_ios_nfc_configuration"][:8]:
            print(f"  - {item}")
        print("  Note: NFC-related iOS files do not imply Multipaz NFC presentment support.")
    if report["warnings"]:
        print("Warnings:")
        for warning in report["warnings"]:
            print(f"  - {warning}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a Kotlin Multiplatform project for Multipaz integration details.")
    parser.add_argument("project_path", nargs="?", default=".", help="Project directory to inspect. Defaults to the current directory.")
    parser.add_argument("--json-only", action="store_true", help="Print JSON only.")
    parser.add_argument("--summary-only", action="store_true", help="Print the human-readable summary only.")
    args = parser.parse_args()

    root = Path(args.project_path).resolve()
    if not root.exists():
        print(f"error: project path does not exist: {root}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"error: project path is not a directory: {root}", file=sys.stderr)
        return 2

    report = build_report(root)

    if not args.json_only:
        print_summary(report)
    if not args.summary_only:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

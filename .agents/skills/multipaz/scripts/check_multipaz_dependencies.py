#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


DIRECT_DEP_RE = re.compile(r'["\'](org\.multipaz:[^:"\']+)(?::([^"\']+))?["\']')
PROJECT_DEP_RE = re.compile(r'project\(\s*":(multipaz[^"]*)"\s*\)')
ANDROID_ONLY_USAGE = [
    "android.nfc.",
    "android.app.Activity",
    "androidx.credentials",
    "org.multipaz.compose.mdoc.MdocNdefService",
    "org.multipaz.compose.mdoc.MdocNfcV2Service",
    "org.multipaz.compose.prompt.PresentmentActivity",
    "org.multipaz.compose.digitalcredentials.CredentialManagerPresentmentActivity",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_current_module_names(root: Path) -> set[str]:
    settings = read_text(root / "settings.gradle.kts") if (root / "settings.gradle.kts").exists() else ""
    modules = set(re.findall(r'include\(":(.*?)"\)', settings))
    artifact_names = set()
    for module in modules:
        artifact_names.add(module.replace(":", "-"))
    artifact_names.update(
        {
            "multipaz",
            "multipaz-compose",
            "multipaz-doctypes",
            "multipaz-utopia",
            "multipaz-longfellow",
            "multipaz-dcapi",
            "multipaz-openid4vci",
            "multipaz-verifier",
            "multipaz-csa",
            "multipaz-cbor-rpc",
            "multipaz-swiftui",
        }
    )
    return artifact_names


def collect_version_catalog_aliases(root: Path) -> dict:
    aliases = {}
    libs_toml = root / "gradle" / "libs.versions.toml"
    if tomllib and libs_toml.exists():
        data = tomllib.loads(libs_toml.read_text(encoding="utf-8"))
        for section_name in ("libraries", "versions"):
            for key, value in data.get(section_name, {}).items():
                text = json.dumps(value) if isinstance(value, dict) else str(value)
                if "multipaz" in text:
                    aliases[f"{section_name}.{key}"] = value
    return aliases


def scan_build_files(root: Path) -> dict:
    results = {}
    versions = {}
    suspicious = []
    known_artifacts = load_current_module_names(root)

    for build_file in sorted(root.rglob("build.gradle.kts")):
        text = read_text(build_file)
        rel = str(build_file.relative_to(root))
        direct = []
        project_deps = []
        for artifact, version in DIRECT_DEP_RE.findall(text):
            name = artifact.split(":", 1)[1]
            direct.append({"artifact": artifact, "version": version or None})
            if version:
                versions.setdefault(artifact, set()).add(version)
            if name.startswith("multipaz") and name not in known_artifacts:
                suspicious.append(
                    {
                        "file": rel,
                        "message": f"Dependency {artifact} does not match the current repository module set",
                    }
                )
        for project_name in PROJECT_DEP_RE.findall(text):
            project_deps.append(project_name)
        if direct or project_deps:
            results[rel] = {"artifacts": direct, "projects": project_deps}

    inconsistent = {
        dep: sorted(list(found_versions))
        for dep, found_versions in versions.items()
        if len(found_versions) > 1
    }
    return {
        "dependencies_by_file": results,
        "inconsistent_versions": inconsistent,
        "suspicious_dependencies": suspicious,
        "version_catalog_aliases": collect_version_catalog_aliases(root),
    }


def scan_android_only_usage(root: Path) -> list[dict]:
    findings = []
    for source_root in root.rglob("src"):
        for forbidden_source_set in ("commonMain", "iosMain", "iosX64Main", "iosArm64Main", "iosSimulatorArm64Main"):
            folder = source_root / forbidden_source_set
            if not folder.exists():
                continue
            for path in folder.rglob("*"):
                if not path.is_file():
                    continue
                if path.suffix not in {".kt", ".kts", ".swift"}:
                    continue
                text = read_text(path)
                for marker in ANDROID_ONLY_USAGE:
                    if marker in text:
                        findings.append(
                            {
                                "file": str(path.relative_to(root)),
                                "source_set": forbidden_source_set,
                                "marker": marker,
                            }
                        )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a project for Multipaz dependency alignment and Android-only API leakage.")
    parser.add_argument("project_path", nargs="?", default=".", help="Project directory to inspect.")
    args = parser.parse_args()

    root = Path(args.project_path).resolve()
    if not root.exists() or not root.is_dir():
        print(f"error: invalid project path: {root}", file=sys.stderr)
        return 2

    report = scan_build_files(root)
    report["android_only_usage_in_shared_or_ios"] = scan_android_only_usage(root)
    report["recommendations"] = []
    if report["inconsistent_versions"]:
        report["recommendations"].append("Align all org.multipaz artifact versions before changing feature code.")
    if report["android_only_usage_in_shared_or_ios"]:
        report["recommendations"].append("Move Android-only presentment or NFC APIs out of commonMain and iOS source sets.")
    if report["suspicious_dependencies"]:
        report["recommendations"].append("Verify whether suspicious dependency names are outdated or incorrect for the current Multipaz version.")

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

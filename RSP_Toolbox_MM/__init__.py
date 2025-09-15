import importlib

# External dependencies to check
_required_packages = {
    "scipy": "scipy",
    "matplotlib": "matplotlib",
    "numpy": "numpy",
    "tqdm": "tqdm",
}

_missing = []
for pkg, import_name in _required_packages.items():
    try:
        importlib.import_module(import_name)
    except ImportError:
        _missing.append(pkg)

if _missing:
    print("The following external packages are missing:", ", ".join(_missing))
    print("Please install them using:")
    print(f"    pip install {' '.join(_missing)}")
"""
依赖检查脚本
检查所有必需的依赖是否正确安装
"""

import sys

def check_dependency(module_name, package_name=None, optional=False):
    """检查单个依赖"""
    if package_name is None:
        package_name = module_name

    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        status = "✓"
        color = "\033[92m"  # Green
        print(f"{color}{status}\033[0m {package_name:20s} {version}")
        return True
    except ImportError:
        if optional:
            status = "○"
            color = "\033[93m"  # Yellow
            print(f"{color}{status}\033[0m {package_name:20s} (可选，未安装)")
        else:
            status = "✗"
            color = "\033[91m"  # Red
            print(f"{color}{status}\033[0m {package_name:20s} (必需，未安装)")
        return optional

def main():
    print("=" * 60)
    print("DreamWaQ Go2 依赖检查")
    print("=" * 60)
    print()

    print("核心依赖:")
    print("-" * 60)
    core_deps = [
        ('mujoco', 'mujoco'),
        ('torch', 'torch'),
        ('numpy', 'numpy'),
        ('scipy', 'scipy'),
        ('pynput', 'pynput'),
    ]

    core_ok = all(check_dependency(mod, pkg) for mod, pkg in core_deps)

    print()
    print("Web界面依赖 (可选):")
    print("-" * 60)
    web_deps = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('websockets', 'websockets'),
    ]

    for mod, pkg in web_deps:
        check_dependency(mod, pkg, optional=True)

    print()
    print("=" * 60)

    if core_ok:
        print("\033[92m✓ 所有核心依赖已安装！可以运行基本仿真。\033[0m")
        print()
        print("运行仿真:")
        print("  python scripts/dreamwaq_go2.py")
        print("  或: start.bat")
    else:
        print("\033[91m✗ 缺少核心依赖！请安装:\033[0m")
        print("  pip install -r requirements-minimal.txt")

    print("=" * 60)

if __name__ == "__main__":
    main()

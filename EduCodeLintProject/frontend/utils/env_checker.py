import subprocess
import sys
import os
import logging
import ctypes

REQUIRED_PACKAGES = [
    "flake8",
    "flake8-json",
    "pep8-naming",
    "pylint",
    "radon",
    "bandit",
    "pyright",
    "pydocstyle"
]


def _get_installed_packages():
    """返回已安装的包名列表（小写）"""
    try:
        result = subprocess.run(
            ["python", "-m", "pip", "list", "--format=freeze"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=0x08000000 if os.name == 'nt' else 0,
            timeout=15
        )
        if result.returncode != 0:
            logging.error(f"pip list 失败: {result.stderr.decode('utf-8', errors='ignore')}")
            return set()

        packages = set()
        output = result.stdout.decode('utf-8', errors='ignore')
        for line in output.splitlines():
            line = line.strip()
            if '==' in line:
                pkg_name = line.split('==')[0].lower()
                packages.add(pkg_name)
        logging.info(f"已安装的包: {packages}")
        return packages
    except Exception as e:
        logging.error(f"获取已安装包列表失败: {e}")
        return set()


def get_missing_packages():
    """返回缺失的包列表"""
    installed = _get_installed_packages()
    missing = []
    for pkg in REQUIRED_PACKAGES:
        if pkg.lower() not in installed:
            missing.append(pkg)
    logging.info(f"缺失的包: {missing}")
    return missing


def _show_console():
    """为当前进程分配一个控制台窗口"""
    if os.name == 'nt' and getattr(sys, 'frozen', False):
        try:
            ctypes.windll.kernel32.AllocConsole()
            sys.stdout = open("CONOUT$", "w")
            sys.stderr = open("CONOUT$", "w")
            return True
        except:
            return False
    return False


def _free_console():
    """释放控制台窗口"""
    if os.name == 'nt' and getattr(sys, 'frozen', False):
        try:
            ctypes.windll.kernel32.FreeConsole()
        except:
            pass


def install_packages(packages):
    """使用 pip 安装指定的包"""
    print(f"\n正在安装必要组件: {', '.join(packages)}")
    print("-" * 50)

    for pkg in packages:
        print(f"\n>>> 正在安装 {pkg}...")
        cmd = [
            "python", "-m", "pip", "install", pkg,
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ]
        result = subprocess.run(
            cmd,
            creationflags=0x08000000 if os.name == 'nt' else 0
        )
        if result.returncode != 0:
            print(f"\n!!! 安装 {pkg} 失败，错误码: {result.returncode}")
            return False
        print(f">>> {pkg} 安装完成！")

    print("\n" + "=" * 50)
    print("所有组件安装完成！")
    return True


def check_environment():
    """
    检查环境，如果需要则自动安装。
    """
    try:
        missing = get_missing_packages()
        if not missing:
            logging.info("环境检测通过")
            return True

        logging.info(f"检测到缺少: {missing}")

        console_allocated = _show_console()

        print("\n" + "=" * 50)
        print("EduCodeLint - 首次运行环境配置")
        print("=" * 50)
        print(f"\n检测到缺少以下组件:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\n正在自动安装，请稍候...")

        success = install_packages(missing)

        if success:
            print("\n安装完成！请关闭此窗口后重新启动程序。")
        else:
            print(f"\n自动安装失败，请手动执行: pip install {' '.join(missing)}")

        print("\n按任意键关闭此窗口...")

        try:
            import msvcrt
            msvcrt.getch()
        except:
            input()

        if console_allocated:
            _free_console()

        return False

    except Exception as e:
        logging.error(f"环境检测异常: {e}")
        return True

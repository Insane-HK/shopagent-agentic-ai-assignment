"""
Build script — packages Lambda deployment zip without needing Docker or matching Python version.
Installs deps into a build folder, copies source code, creates zip.
"""
import os, shutil, subprocess, sys, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(ROOT, ".build")
ZIP_PATH = os.path.join(ROOT, "lambda_package.zip")

def clean():
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

def install_deps():
    os.makedirs(BUILD_DIR, exist_ok=True)
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "-r", os.path.join(ROOT, "requirements.txt"),
        "-t", BUILD_DIR,
        "--no-user",
        "--quiet",
        "--platform", "manylinux2014_x86_64",
        "--python-version", "3.12",
        "--only-binary=:all:",
        "--implementation", "cp",
    ])

def copy_source():
    # copy agent package
    src_agent = os.path.join(ROOT, "agent")
    dst_agent = os.path.join(BUILD_DIR, "agent")
    if os.path.exists(dst_agent):
        shutil.rmtree(dst_agent)
    shutil.copytree(src_agent, dst_agent)

    # copy app package
    src_app = os.path.join(ROOT, "app")
    dst_app = os.path.join(BUILD_DIR, "app")
    if os.path.exists(dst_app):
        shutil.rmtree(dst_app)
    shutil.copytree(src_app, dst_app)

    # copy lambda handler
    shutil.copy2(os.path.join(ROOT, "lambda_handler.py"), BUILD_DIR)

def make_zip():
    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(BUILD_DIR):
            # skip __pycache__
            dirnames[:] = [d for d in dirnames if d != '__pycache__']
            for f in filenames:
                if f.endswith('.pyc'):
                    continue
                full = os.path.join(dirpath, f)
                arcname = os.path.relpath(full, BUILD_DIR)
                zf.write(full, arcname)
    print(f"Created {ZIP_PATH} ({os.path.getsize(ZIP_PATH) / 1024 / 1024:.1f} MB)")

if __name__ == "__main__":
    print("Cleaning...")
    clean()
    print("Installing dependencies...")
    install_deps()
    print("Copying source code...")
    copy_source()
    print("Creating zip...")
    make_zip()
    print("Done! Ready to deploy.")

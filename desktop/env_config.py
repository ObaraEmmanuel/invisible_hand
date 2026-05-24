"""
Build and extract binary upload configuration from platformio environment dump
"""
import shutil
import subprocess
import json
import os
from pathlib import Path

import re

print("Switching to platformio project root: ", Path("..").resolve())
original_path = os.getcwd()
os.chdir("..")

from platformio.project.config import ProjectConfig
config = ProjectConfig()

spec_file = "upload_spec.json"
firmware_folder = Path(original_path) / "firmware"
core_dir = Path(config.get("platformio", "core_dir"))
build_dir = Path(config.get("platformio", "build_dir"))
upload_spec = {}

for env in config.envs():
    print("Budiling firmware for env:", env)
    result = subprocess.run(
        ["pio", "run", "-e", env],
    )

    if result.returncode:
        print(f"Failed to build firmware for env:{env}. Exit code: {result.returncode}")
        print("Skipping env:", env)
        continue

    result = subprocess.run(
        ["pio", "run", "-e", env, "-t", "envdump"],
        capture_output=True,
        text=True
    )

    upload_args = {
        "options": {},
        "images": {}
    }
    if match := re.search(r"\s*UPLOADERFLAGS[\"']\s*:\s*(\[[^\]]*\])", result.stdout, re.DOTALL):
        upload_arg_list = eval(match.group(1))
        current_key = ''
        for arg in upload_arg_list:
            if arg.startswith("-"):
                current_key: str = arg.replace("_", "-")
                upload_args["options"][current_key] = ''
            elif arg.startswith("0x"):
                current_key: str = arg
                upload_args["images"][current_key] = ''
            else:
                if arg == "write_flash":
                    upload_args["options"]["write-flash"] = ''
                    continue
                if current_key.startswith("0x"):
                    upload_args["images"][current_key] = arg
                else:
                    upload_args["options"][current_key] = arg
        upload_spec[env] = upload_args
    else:
        print("Unable to find UPLOADERFLAGS for", env)
        continue

    if match := re.search(r"\s*UPLOAD_SPEED[\"']\s*:\s*(\d+)", result.stdout, re.DOTALL):
        upload_args["options"]['--baud'] = match.group(1)
    if match := re.search(r"\s*BOARD_F_FLASH[\"']?\s*:\s*[\"']?(\d+)", result.stdout, re.DOTALL):
        upload_args["options"]['--flash-freq'] = f"{int(int(match.group(1)) / 1e6)}m"
    if match := re.search(r"\s*BOARD_FLASH_MODE[\"']\s*:\s*[\"']?([^'\"]+)", result.stdout, re.DOTALL):
        upload_args["options"]['--flash-mode'] = match.group(1)
    if match := re.search(r"\s*ESP32_APP_OFFSET[\"']\s*:\s*[\"']?([^'\"]+)", result.stdout, re.DOTALL):
        if inner_match := re.search(r"\s*PROGNAME[\"']\s*:\s*[\"']?([^'\"]+)", result.stdout, re.DOTALL):
            upload_args["images"][match.group(1)] = str(build_dir / env / f"{inner_match.group(1)}.bin")
    if match := re.search(r"\s*UPLOAD_PROTOCOL[\"']\s*:\s*[\"']?([^'\"]+)", result.stdout, re.DOTALL):
        upload_args["tool"] = match.group(1)
    if "--port" in upload_args["options"]:
        upload_args["options"]['--port'] = ""

    print(f"Copying firmware files to firmware/{env}")
    os.makedirs(firmware_folder, exist_ok=True)
    os.makedirs(firmware_folder / env, exist_ok=True)
    for offset, image in upload_args["images"].items():
        image_name = Path(image).name
        print(f"Copying image {image} to firmware/{env}/{image_name}")
        shutil.copy2(image, firmware_folder / env)
        upload_args["images"][offset] = (firmware_folder / env / image_name).relative_to(original_path).as_posix()

    print(f"Spec for env:{env} = {upload_spec[env]}")

print("Switching to script root: ", original_path)
os.chdir(original_path)

if upload_spec:
    print("Writing upload spec to", spec_file)
    with open(spec_file, "w") as f:
        json.dump(upload_spec, f, indent=2)

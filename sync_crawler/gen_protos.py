import os
import subprocess


def generate():
    target_dir = os.path.join("sync_crawler", "protos")
    proto_dir = os.path.join("protos")
    proto_files = [os.path.join(proto_dir, files) for files in os.listdir(proto_dir)]

    command = [
        "python",
        "-m",
        "grpc_tools.protoc",
        f"-I{target_dir}={proto_dir}",
        "--python_out=.",
        "--pyi_out=.",
    ] + proto_files

    subprocess.run(command, shell=False, check=True)

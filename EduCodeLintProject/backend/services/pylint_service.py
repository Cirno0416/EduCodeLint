import json
import os
import subprocess


CONFIG_PATH = '../config/pylintrc_stu'


def run_pylint(file_path: str) -> list:
    rcfile_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), CONFIG_PATH)
    )
    process = subprocess.run(
        [
            'pylint',
            file_path,
            f'--rcfile={rcfile_path}',
            '--output-format=json',
            '--score=no'
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if not process.stdout.strip():
        print("Pylint error output:", process.stderr)
        return []

    try:
        print(process.stdout)
        return json.loads(process.stdout)
    except json.JSONDecodeError:
        print("Failed to parse pylint output as JSON")
        return []

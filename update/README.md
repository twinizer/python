# update/

Scripts for version updating, change management, and package publishing.

## Contents
- `version.sh` — main script for version updating and package publishing
- `src.py` — script for updating version numbers in source files
- `changelog.py` — script for generating and updating the CHANGELOG.md file
- `git.sh` — script for publishing a new version to GitHub
- `pypi.sh` — script for publishing the package to PyPI
- `env_manager.py` — module for managing project configuration
- `config.py` — configuration module for update scripts

## Project Configuration

Project configuration is stored in the `.env` file in the project's root directory. This file is created automatically when the scripts are first run, based on the `.env.example` file.

Available configuration variables:
- `PROJECT_NAME` — project name
- `PACKAGE_PATH` — path to the package directory (relative to the project root directory)

If the `.env` file does not exist or variables are not defined, the scripts will try to detect values automatically or ask the user.

## Usage

To update the version and publish the package:

```bash
# Run the main update script
bash update/version.sh
```

The script will perform the following operations:
1. Load project configuration from the `.env` file or ask the user
2. Create and activate a virtual environment
3. Update the version number in source files
4. Generate an entry in CHANGELOG.md
5. Publish changes to GitHub
6. Publish the package to PyPI

## Troubleshooting

If an error occurs during GitHub publication:
```
Updates were rejected because the remote contains work that you do not have locally
```

You should perform `git pull` before running the script again:
```bash
git pull
bash update/version.sh
```

If the tag already exists:
```
fatal: tag 'vX.Y.Z' already exists
```

You should delete the existing tag before running the script again:
```bash
git tag -d vX.Y.Z
git push origin --delete vX.Y.Z
bash update/version.sh
```

## Configuration Management

To manually create or update the `.env` file:

```bash
python update/env_manager.py
```

The script will display the current project configuration and create the `.env` file if it doesn't exist.

## Polish Documentation

Polish version of this documentation is available in the `update/pl/readme.md` file.

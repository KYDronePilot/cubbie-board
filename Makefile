# Path to the python interpreter.
PYTHON_PATH="$(/usr/bin/env python2.7)"
# Directory to bash interpreter.
BASH_DIR=/bin/bash
# Bin dir to install in.
BIN_DIR=/usr/bin
# Name of the project (and executable).
PROJECT_NAME=cubbieboard
# Full path to main module.
MAIN_MODULE="$(realpath ./cubbie-board/src/main.py)"


# Install the program.
install: copy_project install_init_script


# Copy the program files to a project directory.
copy_project:
	mkdir -p /var/apps/$(PROJECT_NAME)
	rsync -av --progress ./cubbie-board/* /var/apps/$(PROJECT_NAME) --exclude scoreboard_images
	cp .env /var/apps/$(PROJECT_NAME)

# Install Systemd script.
install_init_script:
	cp ./cubbie-board/src/cubbieboard.service /etc/systemd/system/multi-user.target.wants/
	sudo systemctl daemon-reload

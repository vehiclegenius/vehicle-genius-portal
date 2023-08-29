# Only meant to be run once when setting up the project locally
.PHONY: setup
setup:
	pyenv exec python -m venv .pyenv && . .pyenv/bin/activate && pip install --upgrade pip && python -m pip install pip-tools
	chmod +x ./python ./manage

# Run every time the requirements.in changes
# .PHONY: update
# update:
# 	. .pyenv/bin/activate && pip-compile --generate-hashes requirements.in

# Run every time the requirements.txt changes
.PHONY: install
install:
	./python -m pip install -r requirements.txt && ./manage tailwind install

# Runs all the build and run processes in parallel
.PHONY: run
run:
    # Trick to run multiple commands in parallel and kill them all at once
	(trap 'kill 0' SIGINT; make runserver & make tailwind & wait)

.PHONY: runserver
runserver:
	./manage runserver

.PHONY: tailwind
tailwind:
	./manage tailwind start

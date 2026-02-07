SHELL := /bin/bash

PI_HOST := trackbox@trackbox
PI_DEST := ~/trackbox

.PHONY: install uninstall install-service uninstall-service deploy dev clean run

install:
	sudo pip install --break-system-packages --root-user-action=ignore --no-cache-dir --force-reinstall .

uninstall:
	sudo pip uninstall --break-system-packages --root-user-action=ignore -y trackbox

install-service:
	sudo cp trackbox.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable trackbox
	sudo systemctl start trackbox

uninstall-service:
	sudo systemctl stop trackbox
	sudo systemctl disable trackbox
	sudo rm /etc/systemd/system/trackbox.service
	sudo systemctl daemon-reload

deploy:
	rsync -avz --files-from=<(git ls-files) . $(PI_HOST):$(PI_DEST)

clean:
	rm -rf build/ dist/ *.egg-info trackbox/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +

dev:
	GPIOZERO_PIN_FACTORY=mock trackbox

run:
	trackbox

SHELL := /bin/bash

PI_HOST := trackbox@trackbox
PI_DEST := ~/trackbox

.PHONY: install uninstall install-service uninstall-service deploy dev clean run watch watch-remote

install:
	sudo apt-get install -y libfreetype6-dev libjpeg-dev libopenjp2-7 libtiff5
	sudo pip install --break-system-packages --root-user-action=ignore luma.led_matrix
	sudo pip install --break-system-packages --root-user-action=ignore --no-cache-dir --force-reinstall --no-deps .

uninstall:
	sudo pip uninstall --break-system-packages --root-user-action=ignore -y trackbox

install-service: install
	sudo usermod -aG gpio,spi trackbox
	sudo cp trackbox.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable trackbox
	sudo systemctl restart trackbox

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

watch:
	watch -n 0.2 cat /run/trackbox/condition

watch-remote:
	watch -n 0.2 ssh $(PI_HOST) cat /run/trackbox/condition

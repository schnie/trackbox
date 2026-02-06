PI_HOST := trackbox@trackbox
PI_DEST := ~/trackbox

.PHONY: install install-service deploy dev clean run

install:
	pip install --user .

install-service:
	sudo cp trackbox.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable trackbox
	sudo systemctl start trackbox

deploy:
	rsync -avz --files-from=<(git ls-files) . $(PI_HOST):$(PI_DEST)

clean:
	rm -rf build/ dist/ *.egg-info trackbox/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +

dev:
	GPIOZERO_PIN_FACTORY=mock trackbox

run:
	trackbox

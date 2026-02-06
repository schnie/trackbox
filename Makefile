.PHONY: install install-service dev clean run

install:
	pip install .

install-service:
	sudo cp trackbox.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable trackbox
	sudo systemctl start trackbox

clean:
	rm -rf build/ dist/ *.egg-info trackbox/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +

dev:
	GPIOZERO_PIN_FACTORY=mock trackbox

run:
	trackbox

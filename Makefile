default: build-venv

clean:
	rm -f *.so *.o *.pyc
	rm -rf .venv __pycache__

build-venv: Pipfile.lock
	# Create/Sync the venv from the lock file
	PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --ignore-pipfile

Pipfile.lock: Pipfile
	PIPENV_VENV_IN_PROJECT=1 pipenv lock --pre --python dls-python3

.PHONY: default clean

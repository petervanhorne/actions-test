TESTS = test*.py

.PHONY: all check

all: check

check: $(TESTS)
	pytest --full-trace --disable-pytest-warnings -v $(TESTS)


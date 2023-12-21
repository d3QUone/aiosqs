#!/bin/bash
VERBOSE=1

# Run only unit tests in CI
test:
	poetry run nose2 -s aiosqs --verbosity $(VERBOSE) $(target)

# Run E2E tests locally during development
test_e2e:
	poetry run nose2 -s e2e --verbosity $(VERBOSE) $(target)

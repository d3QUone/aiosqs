#!/bin/bash
VERBOSE=1

test:
	poetry run nose2 --verbosity $(VERBOSE)

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

venv: ## configure .venv
	rm -rf .venv
	virtualenv .venv
	. .venv/bin/activate; pip install -Ur requirements.txt
	

source: # activete virtualenv 
	. .venv/bin/activate

start: ## start locust
	nohup locust -f locustfile.py --host=http://127.0.0.1 &

stop: ## stop locust
	kill $(shell ps aux | grep [l]ocust | awk '{print $$2}')

clean: ## clean all
	rm -rf __pycache__
	rm nohup.out
	rm -rf .venv
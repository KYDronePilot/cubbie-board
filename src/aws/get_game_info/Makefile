PROJECT = get_game_info
VIRTUAL_ENV = env
FUNCTION_NAME = getGameInfo
AWS_REGION = us-east-1
FUNCTION_HANDLER = lambda_handler
LAMBDA_ROLE = arn:aws:iam::024919965614:role/service-role/lambda-basic-role

# Default commands
install: virtual
build: clean_package build_package_temp copy_python remove_unused zip
build_deploy: build lambda_delete lambda_create


virtual:
	@echo "--> Setup and activate virtualenv"
	if test ! -d "$(VIRTUAL_ENV)"; then \
		pip install virtualenv; \
		virtualenv $(VIRTUAL_ENV); \
	fi
	@echo ""

clean_package:
	rm -rf ./package/*

build_package_temp:
	mkdir -p ./package/tmp/lib
	cp -a ./$(PROJECT)/. ./package/tmp/

copy_python:
	if test -d $(VIRTUAL_ENV)/lib; then \
		cp -a $(VIRTUAL_ENV)/lib/python3.7/site-packages/. ./package/tmp/; \
	fi
	if test -d $(VIRTUAL_ENV)/lib64; then \
		cp -a $(VIRTUAL_ENV)/lib64/python3.7/site-packages/. ./package/tmp/; \
	fi

remove_unused:
	rm -rf ./package/tmp/wheel*
	rm -rf ./package/tmp/easy-install*
	rm -rf ./package/tmp/setuptools*

zip:
	cd ./package/tmp && zip -r ../$(PROJECT).zip .

lambda_delete:
	aws lambda delete-function \
		--function-name $(FUNCTION_NAME)

lambda_create:
	aws lambda create-function \
		--region $(AWS_REGION) \
		--function-name $(FUNCTION_NAME) \
		--zip-file fileb://./package/$(PROJECT).zip \
		--role $(LAMBDA_ROLE) \
		--handler $(PROJECT).$(FUNCTION_HANDLER) \
		--runtime python3.7 \
		--timeout 10 \
		--memory-size 128

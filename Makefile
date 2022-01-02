
BUCKET_PREFIX := lacework-alliances
KEY_PREFIX := awsimmersionday
LAMBDA_PREFIX := lambda/
APP_PREFIX := app/
APP_DIR := app
MANIFEST_DIR := manifests
MANIFEST_PREFIX := manifests
SCRIPTS_DIR := scripts
SCRIPTS_PREFIX := scripts
CFT_PREFIX := templates
CFT_DIR := templates

PROFILE ?= ct
REGION ?= us-west-2

BUCKET_NAME ?= service_not_defined
BASE = $(shell /bin/pwd)

s3_buckets := $(BUCKET_PREFIX)

TOPTARGETS := all clean package build

LAMBDA_SUBDIRS := $(wildcard functions/source/*/.)
ZIP_LAMBDA_SUBDIRS := $(wildcard functions/packages/*/.)
ZIP_LAMBDA_FILES := $(shell find $(ZIP_LAMBDA_SUBDIRS) -type f -name '*.zip')

$(TOPTARGETS): $(LAMBDA_SUBDIRS)

$(LAMBDA_SUBDIRS):
	$(MAKE) -C $@ $(MAKECMDGOALS) $(ARGS) BASE="${BASE}"

upload: $(s3_buckets)

$(s3_buckets):
	$(info [+] Uploading artifacts to '$@' bucket)
	@$(MAKE) _upload_templates BUCKET_NAME=$@
	@$(MAKE) _upload_manifests BUCKET_NAME=$@
	@$(MAKE) _upload_scripts BUCKET_NAME=$@
	@$(MAKE) _upload_lambda_zip BUCKET_NAME=$@
	@$(MAKE) _upload_app_zip BUCKET_NAME=$@

_upload_templates:
	$(info [+] Uploading templates to $(BUCKET_NAME) bucket)
	@aws --profile $(PROFILE) --region $(REGION) s3 cp $(CFT_DIR)/ s3://$(BUCKET_NAME)/$(KEY_PREFIX)/$(CFT_PREFIX) --recursive --exclude "*" --include "*.yaml" --include "*.yml" --acl public-read

_upload_manifests:
	$(info [+] Uploading manifests to $(BUCKET_NAME) bucket)
	@aws --profile $(PROFILE) --region $(REGION) s3 cp $(MANIFEST_DIR)/ s3://$(BUCKET_NAME)/$(KEY_PREFIX)/$(MANIFEST_PREFIX) --recursive --exclude "*" --include "*.yaml" --include "*.yml" --acl public-read

_upload_scripts:
	$(info [+] Uploading scripts to $(BUCKET_NAME) bucket)
	@aws --profile $(PROFILE) --region $(REGION) s3 cp $(SCRIPTS_DIR)/ s3://$(BUCKET_NAME)/$(KEY_PREFIX)/$(SCRIPTS_PREFIX) --recursive --exclude "*" --include "*.sh" --acl public-read

_upload_app_zip:
	$(info [+] Uploading app to $(BUCKET_NAME) bucket)
	(cd app && zip -r app.zip . -x "*.DS_Store*" "*.git*" "build*" "package-lock.json" "Makefile" "requirements.txt" "node_modules/*")
	@aws --profile $(PROFILE) --region $(REGION) s3 cp app/app.zip s3://$(BUCKET_NAME)/$(KEY_PREFIX)/$(APP_PREFIX) --acl public-read
	rm -f app/app.zip

_upload_lambda_zip: $(ZIP_LAMBDA_SUBDIRS)

$(ZIP_LAMBDA_SUBDIRS): $(ZIP_LAMBDA_FILES)

$(ZIP_LAMBDA_FILES):
	$(info [+] Uploading lambda zip files to $(BUCKET_NAME) bucket)
	@aws --profile $(PROFILE) --region $(REGION) s3 cp $@ s3://$(BUCKET_NAME)/$(KEY_PREFIX)/$(LAMBDA_PREFIX) --acl public-read

.PHONY: $(TOPTARGETS) $(LAMBDA_SUBDIRS) $(s3_buckets) $(ZIP_LAMBDA_FILES)

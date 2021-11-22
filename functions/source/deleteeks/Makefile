PROJECT = deleteeks
DIR_NAME = deleteeks
FUNCTION = $(PROJECT)
DIST_DIR ?= "$(BASE)"/functions/packages/$(DIR_NAME)

all: build

.PHONY: clean build

clean:
	rm -f $(DIST_DIR)/$(FUNCTION).zip || true
	rm -rf build

build: clean
	mkdir build
	cp  *.py build/
	pip install -r requirements.txt -t build/
	cd build; zip -r $(DIST_DIR)/$(FUNCTION).zip .
	rm -rf build

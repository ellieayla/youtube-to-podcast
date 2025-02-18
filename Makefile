

.PHONY: update-git
update-git:
	git fetch
	git pull

# only recent items
.PHONY: fetch
fetch:
	yt-dlp --dateafter today-1month --config-locations yt-dlp.conf

.PHONY: fetch-all
fetch-all:
	yt-dlp --config-locations yt-dlp.conf


.PHONY: index
index:
	python make-index.py _audio --overwrite

.PHONY: static
static:
	bundle exec jekyll serve --force_polling

.PHONY: clean
clean:
	rm -rf YouTube

.PHONY: expose
expose:
	tailscale funnel 4000

.PHONY: build
build:
	bundle exec jekyll build

.PHONY: all
all: update-git fetch index build


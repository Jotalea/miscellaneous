APP          := piskel-term
GO           := go
GOFLAGS      ?=
GOOS         ?=linux
GOARCH       ?=amd64
HALF_BLOCKS  ?=0
DIST         := dist
BINARY       := $(DIST)/$(APP)

ifeq ($(HALF_BLOCKS),1)
RENDER_FLAGS := --half-blocks
else
RENDER_FLAGS :=
endif

.PHONY: all init deps fmt vet test build static verify run clean clean-export

all: static

init:
	@test -f go.mod || $(GO) mod init piskelterm

# Fetch the terminal dependency and normalize the module graph.
deps: init
	$(GO) get golang.org/x/term@latest
	$(GO) mod tidy

fmt:
	gofmt -w main.go

vet: fmt
	$(GO) vet ./...

test: vet
	$(GO) test ./...

build: fmt
	@mkdir -p $(DIST)
	$(GO) build $(GOFLAGS) -trimpath -o $(BINARY) main.go

static: fmt
	@mkdir -p $(DIST)
	CGO_ENABLED=0 GOOS=$(GOOS) GOARCH=$(GOARCH) $(GO) build $(GOFLAGS) -trimpath -ldflags="-s -w" -o $(BINARY) main.go

verify: static
	file $(BINARY)
	ldd $(BINARY) || true
	@test "$$(file -b $(BINARY) | grep -ci 'statically linked')" -gt 0

# Examples:
#   make run
#   make run HALF_BLOCKS=1 ARGS="64 32"
#   make run ARGS="--half-blocks 64 32"
run: build
	$(BINARY) $(RENDER_FLAGS) $(ARGS)

clean-export:
	rm -f piskel-term.ansi piskel-term.unicode

clean:
	rm -rf $(DIST)
	$(MAKE) clean-export

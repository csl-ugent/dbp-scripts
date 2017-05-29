CPPFLAGS ?= -g -Wall -Werror -O3 -fomit-frame-pointer -march=native
CXXFLAGS ?= -std=c++0x

# Get LLVM stuff for SP
sp: CPPFLAGS += $(shell ${LLVM_DIR}/bin/llvm-config --cppflags)
sp: CXXFLAGS += $(shell ${LLVM_DIR}/bin/llvm-config --cxxflags)
sp: LDFLAGS += $(shell ${LLVM_DIR}/bin/llvm-config --ldflags)
sp: LDLIBS += $(shell ${LLVM_DIR}/bin/llvm-config --libs support)

.PHONY: all clean
all: nop sp

clean:
	rm nop sp

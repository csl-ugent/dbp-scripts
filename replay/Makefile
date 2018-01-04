CPPFLAGS ?= -g -Wall -Werror -O3 -fomit-frame-pointer -march=native
CXXFLAGS ?= -std=c++0x

# Get LLVM stuff for SP
nop sp: CPPFLAGS += $(shell ${LLVM_DIR}/bin/llvm-config --cppflags)
nop sp: CXXFLAGS += $(shell ${LLVM_DIR}/bin/llvm-config --cxxflags)
nop sp: LDFLAGS += $(shell ${LLVM_DIR}/bin/llvm-config --ldflags)
nop sp: LDLIBS += $(shell ${LLVM_DIR}/bin/llvm-config --libs support)

.PHONY: all clean
all: nop sp

clean:
	rm nop sp

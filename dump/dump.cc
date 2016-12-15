#include "client/linux/handler/exception_handler.h"

/* Write the path of the dump to stderr and immediately flush it */
static bool dumpCallback(const google_breakpad::MinidumpDescriptor& descriptor, void* context, bool succeeded)
{
  fprintf(stderr, "DBP_DUMP_PATH: %s\n", descriptor.path());
  fflush(stderr);
  return succeeded;
}

google_breakpad::MinidumpDescriptor descriptor("/tmp");
google_breakpad::ExceptionHandler eh(descriptor, NULL, dumpCallback, NULL, true, -1);

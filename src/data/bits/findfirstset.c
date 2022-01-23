// Source:
// https://codegolf.stackexchange.com/a/103531
#define _GNU_SOURCE  // request that string.h define ffsl
#include <stdint.h>
#include <stdlib.h>

#ifdef __unix__
// https://stackoverflow.com/questions/11350878/how-can-i-determine-if-the-operating-system-is-posix-in-c
#include <unistd.h>  // for _POSIX_VERSION
#endif

#ifdef _POSIX_VERSION
#include <strings.h>
#include <string.h>  // for GNU-extension ffsl in case we want that
int bit_position_posix(uint32_t v) {
#ifdef __GNUC__
  // tell the compiler about the assumption that v!=0
  // unfortunately doesn't help gcc or clang make better ffs() code :(  And ICC makes worse code
  if (v == 0)
    __builtin_unreachable();
#endif

  return ffs(v);
}
#endif

#ifdef __GNUC__
static inline
  int bit_position_gnu(uint32_t v) {
  // v is guaranteed to be non-zero, so we can use a function that's undefined in that case

  // we can count from the front or back, since there's only one bit set
  // but the compiler doesn't know this so we use macros to select a method that doesn't e.g. require an RBIT instruction on ARM

  // TODO: tweak this for more architectures
#if (defined(__i386__) || defined(__x86_64__))
  return __builtin_ctz(v) + 1;
#else
  return 32 - __builtin_clz(v) + 1;
#endif
}
#endif

#ifdef _MSC_VER
// https://msdn.microsoft.com/en-us/library/wfd9z0bb.aspx
#include <intrin.h>
int bit_position_msvc(uint32_t v) {
  unsigned long idx;
  int nonzero = _BitScanForward(&idx, v);
  return idx + 1;
}
#endif

static inline
  int findfirstset(uint32_t v)
{
#ifdef __GNUC__
  return bit_position_gnu(v);
#elif defined(_MSC_VER)
  return bit_position_msvc(v);
#elif defined(_POSIX_VERSION)
  return bit_position_posix(v);
#else
  #error no good bitscan detected for this platform
#endif
}

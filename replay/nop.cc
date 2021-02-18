#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <random>
#include <sstream>
#include <string>

/* Include the LLVM header required to get the hashing functions */
#include "llvm/ADT/Hashing.h"

uint32_t align(uint32_t x, uint32_t base)
{
  uint32_t remainder = x % base;
  if (remainder == 0)
    return x;

  return x + base - remainder;
}

int main(int argc, char** argv) {
  /* Decode arguments */
  if (argc != 5) {
    std::cerr << "ARGUMENTS: ./binary <seed> <chance> <build_prefix> <file>" << std::endl;
    return -1;
  }
  const uint32_t seed = std::stoul(argv[1]);
  const uint32_t chance = std::stoul(argv[2]);
  const std::string& build_prefix = argv[3];
  std::uniform_int_distribution<unsigned> pct_distribution(0,99);

  /* Open file and read line per line */
  std::ifstream input(argv[4]);
  std::string line;
  std::mt19937 fun_rng;
  uint32_t offset = 0, offset_diff = 0;
  bool outputting = false;
  while (std::getline(input, line)) {
    /* Differentiate between function record and BBL record */
    if (line.find(' ') != std::string::npos) {
      /* In case we're dealing with a function record: get the names from the line */
      std::istringstream iss(line);
      std::string filename, function_name;
      iss >> filename >> function_name;

      // Create the seed and PRNG for the function. We create a function-specific seed from
      // the root seed by XORing the root with the hash value of the function name.
      fun_rng.seed(seed ^ llvm::hash_value(function_name));
      offset = 0;
      offset_diff = 0;
      outputting = true;

      /* Adapt and combine the filename and function name to look like obj_name:section_name */
      size_t i = filename.rfind('.');
      filename.replace(i + 1, filename.length(), "o");
      if (function_name.find("_GLOBAL__sub_I_") == 0)/* Startup sections have functions with a weird prefix */
        function_name = "startup";

      /* Differentiate between when the build prefix is an archive, and when it is a normal path */
      if (build_prefix.compare(build_prefix.length() -2, 2, ".a") == 0)
      {
        /* We want to output this in the form of archive.a(object.o):.text. */
        size_t pos = filename.find_last_of('/');

        /* We will ignore (that is, not output) simple filenames without a path structure */
        if (pos == std::string::npos)
        {
          outputting = false;
          continue;
        }

        filename = filename.substr(pos +1);
        std::cout << build_prefix << "(" << filename << "):.text." << function_name << std::endl;
      }
      else
        std::cout << build_prefix << "/" << filename << ":.text." << function_name << std::endl;
    }
    else if (outputting)
    {
      const unsigned colon_loc = line.find(':');
      if (line[0] == 'D' || line[0] == 'I')
      {
        const uint32_t nr_of_ins = std::stoul(line.substr(1, colon_loc));
        uint32_t alignment = std::stoul(line.substr(colon_loc +1));
        if (alignment)
        {
          alignment = pow(2, alignment);

          /* Calculate the change in padding (with some intermediate calculations) */
          const uint32_t original_padding = align(offset, alignment) - offset;
          const uint32_t new_offset = offset + offset_diff;
          const uint32_t new_padding = align(new_offset, alignment) - new_offset;
          const int32_t padding_change = new_padding - original_padding;

          /* If there's any change in padding, communicate this to the invoking scripts */
          if (padding_change > 0)
            std::cout << std::hex << offset << ' ' << std::hex << padding_change << std::endl;
          if (padding_change < 0)
            std::cout << std::hex << offset << " -" << std::hex << -padding_change << std::endl;

          /* Update the offset with the expected padding */
          offset_diff += padding_change;
          offset += original_padding;
        }

        offset += 4 * nr_of_ins;
      }
      else {
        /* Find out how many instructions there are in the BBL, and create the RNG */
        const unsigned colon_loc = line.find(':');
        const uint32_t nr_of_ins = std::stoul(line.substr(0, colon_loc));
        std::mt19937 bbl_rng(fun_rng());

        for (uint32_t iii = 0; iii < nr_of_ins; iii++, offset += 4)
        {
          if (pct_distribution(bbl_rng) < chance)
          {
            std::cout << std::hex << offset << ' ' << std::hex << 4 << std::endl;
            offset_diff += 4;
          }
        }
      }
    }
  }
  input.close();
}

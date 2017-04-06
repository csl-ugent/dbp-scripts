#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <random>
#include <sstream>
#include <string>

int main(int argc, char** argv) {
  /* Decode arguments */
  if (argc != 4) {
    std::cerr << "ARGUMENTS: ./binary <seed> <chance> <file>" << std::endl;
    return -1;
  }
  const uint32_t seed = std::stoul(argv[1]);
  const uint32_t chance = std::stoul(argv[2]);

  /* Open file and read line per line */
  std::uniform_int_distribution<uint32_t> pct_distribution(0, 99);
  std::mt19937 rng_bbl_seeder;
  std::ifstream input(argv[3]);
  std::string line;
  while (std::getline(input, line)) {
    /* If the line doesn't contain a space it's a path. If it's the path to an object in an archive,
     * we'll rewrite it so that it conforms to how our python scripts expect this to look:
     * archive.a(obj.o):.text_section (instead of archive.a:obj.o:.text_section)
     */
    if (line.find(' ') == std::string::npos) {
      /* Reseed the BBL seeder RNG for this path */
      std::string hash_str = line.substr(line.find_last_of('/'));
      size_t hash = std::hash<std::string>{}(hash_str);
      rng_bbl_seeder.seed(seed ^ hash);

      size_t lpos = line.find_first_of(':');
      size_t rpos = line.find_last_of(':');
      if (lpos != rpos) {
          line[lpos] = '(';
          line.insert(rpos, 1, ')');
      }
      std::cout << line << std::endl;
      continue;
    }
    /* Else we extract the address and number of instructions of the BBL */
    else {
      std::istringstream iss(line);
      uint32_t offset, nins;
      iss >> std::hex >> offset >> std::dec >> nins;

      /* Create the RNG for this BBL and check for every instruction whether a NOP was inserted */
      std::mt19937 rng_do_apply(rng_bbl_seeder());
      for (uint32_t iii = 1 ; iii < nins; iii++) {
        if (pct_distribution(rng_do_apply) < chance)
          std::cout << std::hex << (offset + 4 * (iii -1)) << std::endl;
      }
    }
  }
  input.close();
}

#include <random>
#include <iostream>
#include <fstream>

// compile as g++ -std=c++0x -o replay ../frontends/nop-replay.cc


using namespace std;

int main(int argc, char** argv) {
  if (argc != 4) {
    cerr << "ARGUMENTS: ./nop-replay <seed> <chance> <file>" << endl;
    return -1;
  }
  
  int seed = atoi(argv[1]);
  int chance = atoi(argv[2]);
  
  //cout << "Replaying: seed = " << seed << ", chance = " << chance << endl;

  std::mt19937 rng_bbl_seeder(seed);
  std::uniform_int_distribution<uint32_t> pct_distribution(0, 99);

  ifstream input;
  input.open(argv[3]);

  while (input) {
    long address;
    long nins;

    if (! (input >> hex >> address))
      break;
    input.get();
    input >> dec >> nins;
    //cout << "Read: " << hex << address << dec << "," << nins << endl;

    std::mt19937 rng_do_apply( rng_bbl_seeder() );

    for (int i = 1 ; i < nins; i++) {
      if (pct_distribution(rng_do_apply) >= chance) {
        continue;
      }
      cout << "Old  0x" << hex << (address + 4*(i-1)) << endl;
    }

    if (input.get() != '\n') {
      break;
    }
  }
}


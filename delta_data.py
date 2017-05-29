import bz2
import gnupg
import subprocess

# Import own modules
import config
import seed

section_name = '.delta_data'

# Encode the seeds and patch into the encrypted, signed delta data. The patch should be in binary,
# and the return is also binary.
def encode(seeds, patch, encrypt=True):
    # Start with the seeds as 4-byte unsigned little-endian
    dd = bytes()
    for seed in seeds:
        dd += int(seed).to_bytes(4, byteorder='little')

    # Compress the patch and add it
    if patch:
        dd += bz2.compress(patch)

    if not encrypt:
        return dd
    else:
        # Encrypt and sign it
        gpg = gnupg.GPG(gnupghome=config.gpg_dir)
        keys = gpg.list_keys(secret=True)
        assert len(keys) == 1, 'We only support one secret key at a time!'
        fingerprint = keys[0]['fingerprint']
        dd_enc = gpg.encrypt(dd, fingerprint, armor=False)
        return dd_enc.data

# Decode the delta data back into the seeds (of types provided) and patch. This takes binary data and
# returns a binary patch.
def decode(dd_enc, seed_types, encrypt=True):
    if encrypt:
        # Decrypt and verify the delta data
        gpg = gnupg.GPG(gnupghome=config.gpg_dir)
        dd_dec = gpg.decrypt(dd_enc, passphrase=config.gpg_passphrase)
        assert dd_dec.trust_level is not None and dd_dec.trust_level >= dd_dec.TRUST_FULLY, 'Delta data could not be verified!'
        dd = dd_dec.data
    else:
        dd = dd_enc

    # Get the seeds
    nr_of_seeds = len(seed_types)
    int_seeds = []
    for iii in range(nr_of_seeds):
        int_seeds.append(int.from_bytes(dd[iii * 4: (iii +1) * 4], byteorder='little'))
    seeds = [cls(s) for cls, s in zip(seed_types, int_seeds)]

    # Get the patch and decompress it
    compressed_patch = dd[nr_of_seeds * 4:]
    if compressed_patch:
        patch = bz2.decompress(compressed_patch)
    else:
        patch = bytes()

    return (seeds, patch)

# Injects the delta data into a separate section in the binary.
# The delta data is in a file for easier objcopy use.
def inject(binary, dd_path):
    subprocess.check_call([config.objcopy_bin, '--add-section', section_name + '=' + dd_path, binary])

# Extracts the delta data from the separate section in the binary.
# The data returned is binary.
def extract(binary):
    pass

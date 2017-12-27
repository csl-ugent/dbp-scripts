import os
import subprocess

# Import own modules
import config
import support
from seed import AbstractSeed

class SPSeed(AbstractSeed):
    """The class for SP seeds"""
    idx = len(AbstractSeed.__subclasses__())

    def replay(seed, base_symfile, base_data):
        print('************ Replaying stack padding. **********')

        # Use the replay tool to find the stack offset for every function
        sections = {}
        for line in subprocess.check_output([os.path.join(config.replay_dir, 'sp'), str(seed), str(config.max_padding),
            os.readlink(os.path.join(base_data, 'build')), os.path.join(base_data, 'stackpadding.list')], universal_newlines=True).splitlines():

            # Split the line and decode the tokens
            tokens = line.split()
            name = tokens[0]
            offset = int(tokens[1])

            # Add the section with the introduced diff
            assert name not in sections, 'Duplicate section!'
            sections[name] = offset

        # Use the replay tool again, but this time for the extra source code that was built
        for line in subprocess.check_output([os.path.join(config.replay_dir, 'sp'), str(seed), str(config.max_padding),
            os.path.join(support.create_path_for_seeds(config.extra_build_dir), config.breakpad_archive), os.path.join(os.path.dirname(base_data), 'stackpadding.list')], universal_newlines=True).splitlines():

            # Split the line and decode the tokens
            tokens = line.split()
            name = tokens[0]
            offset = int(tokens[1])

            # Add the section with the introduced diff
            assert name not in sections, 'Duplicate section!'
            sections[name] = offset

        for func in base_symfile.funcs:
            # Get the stack offset introduced
            offset = sections.get(func.section_name, 0)

            if offset:
                base_record = func.get_stack_offset_record()
                # This record may very well not exist, such as when a frame pointer is used.
                if base_record:
                    base_record.set_frame_size(base_record.get_frame_size() + offset - config.default_padding)

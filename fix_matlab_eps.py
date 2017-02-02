#!/usr/bin/env python3
""" Fix EPS images that contain artifacts since Matlab 2014b

Usage: python fix_matlab_eps.py input-file output-file inkscape-binary-path

See inkscape command line documentation here: https://inkscape.org/en/doc/inkscape-man.html
"""

import re
import os
import sys
from subprocess import PIPE, run
import tempfile


def main():

    if len(sys.argv) >= 4:
        inkscape_path = sys.argv[3]
    else:
        inkscape_path = 'inkscape'  # Assume the Inkscape binary is in PATH

    ret = run(inkscape_path + ' --version', stdout=PIPE, stderr=PIPE, shell=True)

    if len(sys.argv) < 3:
        print('Usage: python fix_matlab_eps.py input-file output-file inkscape-binary-path')

    if ret.returncode:
        print('Error: You need Inkscape to convert images to a parsable format')
        return

    ver = str(ret.stdout, 'utf-8').split(' ')[1]  # Store the Inkscape version for later
    tmp = os.path.join(tempfile.gettempdir(), 'fix_matlab_eps.eps')
    ret = run('"' + inkscape_path + '" --file="' + sys.argv[1] + '" --export-area-snap -E "' + tmp + '"',
              stdout=PIPE, stderr=PIPE, shell=True)
    # -E FILENAME, --export-eps=FILENAME; -z, --without-gui

    text = ''
    line_list = []
    line = []

    colored_patch = False

    colorbar = False
    first_colorbar = []

    f = open(tmp)
    for i in f.readlines():
        # Ignore ends of patches because we find them manually
        if colored_patch and re.match('.* m f', i):
            continue

        # Hold the patches to group them together
        if colored_patch and re.match('.* f', i):
            line.append(i.replace('f', 'h'))
            line_list.append(line)
            line = []
            continue

        # End of patches with 1 color
        if colored_patch and (re.match('.* r?g$', i) or re.match('^Q Q$', i)) \
           and line_list:
            colored_patch = False
            last = []
            for j in reversed(line_list):
                for k in last:
                    text += k
                last = j
            for k in last[:-1]:
                text += k
            text += last[-1].replace('h\n', 'f\n')
            line_list = []
        elif re.match('.* r?g$', i) or i.endswith('showpage\n'):
            colorbar = False
            colored_patch = False

            if line:
                line_list.append(line)
                line = []

            for j in line_list:
                for k in j:
                    text += k
            line_list = []

        # Patches belonging to 1 color
        if re.match('.* rg$', i):
            colored_patch = True
            text += i
            continue

        # Start of the colorbar
        if re.match('^Q q$', i):
            colorbar = True
            line_list.append(i)
            continue

        # Just append any lines of the colorbar
        if colorbar:
            line_list.append(i)

        # End of the colorbar
        if line_list[-3:] == ['Q\n', '  Q\n', 'Q\n']:
            colorbar = False
            if first_colorbar:
                for j in line_list:
                    if j.endswith(' h\n'):
                        for k in first_colorbar:
                            if k.endswith(' h\n'):
                                text += k
                    text += j
                first_colorbar = []
            else:
                first_colorbar = list(line_list)
            line_list = []
            continue

        # There was only one colorbar
        if not colorbar and first_colorbar:
            for j in first_colorbar:
                text += j
            first_colorbar = []

        # Add other stuff
        if colored_patch:
            line.append(i)
            if i.endswith(' h\n') or i.endswith(' f\n'):
                line_list.append(line)
                line = []
        elif not colorbar:
            text += i

    f.close()

    f = open(sys.argv[2], 'w')
    f.write(text)
    f.close()

if __name__ == '__main__':
    main()

"""
String helpers for map labels (MODIFIED from tfprop_sompy.utils.strings).

Original author: Gota Kikugawa / Yuta Nishimura (Tohoku University), Apache-2.0.
Vendored and lightly adjusted (c) 2026 Cameron B. Renteria for use by the
modified visualization engine. See ../engine/ACKNOWLEDGMENTS.md and NOTICE.

``str_wrap_chem`` inserts line breaks into long chemical-compound names so they
fit on a SOM cluster map. It is retained from the upstream thermo-fluid tool; for
the enamel dataset (whose point labels are short tooth/specimen codes) it is a
no-op-ish convenience and is only invoked when label plotting is enabled.
"""

import re


def str_wrap_chem(word):

    # replace space with linebreak
    word = word.replace(' ', '\n')

    # if find cyclo, fluoro, bromo, fluoro, bromo, or hydro,
    #     linebreak after that
    pattern = r'cyclo|chloro|bromo|fluoro|hydro'
    match = re.search(pattern, word, re.IGNORECASE)
    if match:
        word = word[:match.start()] + word[match.start():match.end()] \
            + '-\n' + word[match.end():]

    # if find methyl with any subsequent letter, linebreak after that
    pattern = r'methyl.'
    match = re.search(pattern, word, re.IGNORECASE)
    if match:
        word = word[:match.start()] + word[match.start():match.end()-1] \
            + '-\n' + word[match.end()-1:]

    return word

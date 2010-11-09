#!/bin/bash

# dict.sh -- google dictionary script
# Copyright (C) 2010 Alexander Lopatin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

# TODO: show "did you mean" words if available

STR=$(echo -n $@ | sed -e 's/ /%20/g')
URL="http://www.google.com/dictionary?q=$STR\
&hl=ru&langpair=en|ru&spell=1&oi=spell"
lynx --source $URL |
    egrep 'span.*dct-..">.*(<\/span>|)$' |
    sed -e 's/<span class="dct-..">//g;s/<\/span>//g;s/&nbsp;/ /g' |
    egrep -v '(dct-elb|a href)'


sed -e 's/\(^\| \)aexp-medium\( \|,\|$\)/\1aexp-ubuntu-latest-medium\2/g' \
    -e 's/\(^\| \)aexp-ubuntu-latest\( \|,\|$\)/\1aexp-ubuntu-latest-medium\2/g' input_file
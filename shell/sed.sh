find . -type f -exec sed -i '
  s/\[\s*self-hosted,\s*/[ /g;     # Handles self-hosted at the beginning within brackets
  s/,\s*self-hosted\s*\]/ ]/g;     # Handles self-hosted at the end within brackets
  s/,\s*self-hosted\s*/ /g;        # Handles self-hosted in the middle
  s/self-hosted,\s*/ /g;           # Handles self-hosted at the beginning without brackets
  s/self-hosted\s*//g              # Handles self-hosted when alone
' {} +

find . -type f -exec sed -i 's/\[\s*self-hosted,\s*/[ /g; s/,\s*self-hosted\s*/ /g; s/self-hosted,\s*/ /g; s/self-hosted\s*/ /g' {} +
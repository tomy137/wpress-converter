# wpress-converter
Tools to unpack .wpress file to folder then folder to .wpress. 

Thanks to https://github.com/ofhouse/wpress-extract for inspiration.

# How to unpack
```
python unpack.py src.wpress output
```

# How to re-pack
```
python repack.py output new.wpress
```

# Warnings
New files will not be added to the repack.wpress. Modified files will be here. That's the main point. 
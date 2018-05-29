# Py-Circos
## Visualize Antibody Clones as Circos Plots

This script was made to convert spreadsheets of antibody clones into circos plots, with different colors representing phenotypic characteristics of the antibody clones.

![example](example.png)

I've included my circos configuration files which use fonts that are not included in the Circos Plot package.  Circos supports true type (.ttf) and open type (.otf) fonts, which can be added to the Circos package (fonts/modern/). To use an added font you must add a key term to the Circos fonts file (etc/fonts.conf) and the path to the font (e.g. aral_bold = fonts/modern/Arial Bold.ttf).

ToDo:
- Add example data
- Create py_circos module of functions
- Lock package dependencies
- Web GUI

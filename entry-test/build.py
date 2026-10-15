# Builds the entry test page: entry-app-src.html with entry-gen.js inlined at /*__GEN__*/ -> sterling-entry-test.html
import os
D = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(D, 'entry-app-src.html')).read().replace('/*__GEN__*/', open(os.path.join(D, 'entry-gen.js')).read())
open(os.path.join(D, 'sterling-entry-test.html'), 'w').write(s); print('built')

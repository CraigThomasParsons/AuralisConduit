import sys
import os
# Add bin to path to simulate the actual script correctly if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'bin')))
from lib.parser import extract_snippet_files

text = """
Here's the application javascript:
```javascript
// file: app.js
console.log('E2E Testing Works');
```

And a fallback code block:
```css
body { margin: 0; }
```
"""

snippets = extract_snippet_files(text)
print(f"Snippets found: {len(snippets)}")
for s in snippets:
    print(s.filename)

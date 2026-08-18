import unittest
# Import our core snippet extraction engine to isolate testing on parser logic
from bin.lib.parser import extract_snippet_files


class TestParserSnippets(unittest.TestCase):
    """
    Test suite to validate the markdown snippet extractor heuristics,
    simulating various ChatGPT return payloads.
    """

    def test_extract_snippets_with_surrounding_text(self):
        """
        Validates that a filename is extracted successfully from the natural language
        sentence immediately preceding the fenced code block.
        """
        # Create a mock ChatGPT response containing a conversational filename
        # right before a Python fenced code block.
        text = '''
Here is the code for `app.py`:
```python
print("Hello World")
```
        '''
        
        # Pass the mock string into our engine to parse actions
        snippets = extract_snippet_files(text)
        
        # Verify exactly one snippet was identified
        self.assertEqual(len(snippets), 1)
        
        # Verify the guessed filename matches the conversational context
        self.assertEqual(snippets[0].filename, "app.py")
        
        # Confirm the heuristic that matched this was 'surrounding_text' (medium confidence)
        self.assertEqual(snippets[0].detection_method, "surrounding_text")
        self.assertEqual(snippets[0].confidence, "medium")

    def test_extract_snippets_with_header_comment(self):
        """
        Validates that a filename is extracted successfully from an inline 
        comment located in the first few lines of the code block.
        """
        # Create a mock javascript snippet representing a high-confidence match
        text = '''
```javascript
// file: main.js
console.log("Hello");
```
        '''
        
        # Hand off string payload to the extraction engine
        snippets = extract_snippet_files(text)
        
        # Verify exactly one snippet was identified
        self.assertEqual(len(snippets), 1)
        
        # Confirm it grabbed 'main.js' properly from the comment
        self.assertEqual(snippets[0].filename, "main.js")
        
        # Confirm the heuristic used was 'inline_comment' (high confidence)
        self.assertEqual(snippets[0].detection_method, "inline_comment")
        self.assertEqual(snippets[0].confidence, "high")

    def test_extract_snippets_fallback(self):
        """
        Validates the fallback system assigns standard sequential names
        to blocks containing no conversational hints or comment headers.
        """
        # Create a mock anonymous CSS block
        text = '''
```css
body { color: red; }
```
        '''
        
        # Initiate extraction process
        snippets = extract_snippet_files(text)
        
        # Ensure block was still captured despite missing metadata
        self.assertEqual(len(snippets), 1)
        
        # Verify the fallback naming convention fired successfully (.css inferred)
        self.assertEqual(snippets[0].filename, "snippet_01.css")
        
        # Confirm we logged exactly why this name was chosen
        self.assertEqual(snippets[0].detection_method, "language_fallback")

    def test_avoid_inline_code(self):
        """
        Ensures standard single-backtick inline code is ignored 
        by our block extraction mechanism.
        """
        # Provide plain paragraph text with embedded inline ticks
        text = '''
Run `npm install` first. Then run `node app.js`. No code blocks here.
        '''
        
        # Perform extraction
        snippets = extract_snippet_files(text)
        
        # Assert no blocks were picked up since they weren't triple-fenced
        self.assertEqual(len(snippets), 0)


# Standard unittest kickoff
if __name__ == '__main__':
    unittest.main()

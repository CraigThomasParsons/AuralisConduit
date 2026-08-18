<?php

namespace Tests\Acceptance;

use Tests\Support\AcceptanceTester;

class SnippetExtractionCest
{
    /**
     * Set up testing requirements before the test executes.
     */
    public function _before(AcceptanceTester $I): void
    {
        // Define directory paths for easier reference
        $inboxDir = __DIR__ . '/../../inbox/codeception_test_1';
        $runsDir = __DIR__ . '/../../runs/codeception_test_1';

        // Clear previous test run output to ensure test purity
        if (is_dir($runsDir)) {
            shell_exec('rm -rf ' . escapeshellarg($runsDir));
        }

        // Generate the fake inbound job directory tree
        if (!is_dir($inboxDir)) {
            mkdir($inboxDir, 0777, true);
        }

        // Establish the mandatory briefing.md to pass validation
        file_put_contents($inboxDir . '/briefing.md', '# Perform Test extraction');
    }

    /**
     * Executes the E2E verification workflow for snippet extraction
     */
    public function verifySnippetExtraction(AcceptanceTester $I): void
    {
        // Formulate a fake successful ChatGPT response payload
        // This includes a JavaScript snippet with a header hint and a CSS fallback
        $mockResponseText = "
Here's the application javascript:
```javascript
// file: app.js
console.log('E2E Testing Works');
```
" . str_pad("", 300, " ") . "
And a fallback code block:
```css
body { margin: 0; }
```
";

        // Wrap the payload properly to emulate the Extension's structure
        $payload = [
            'id' => 'codeception_test_1',
            'response' => $mockResponseText,
            'debug' => 'Codeception test suite execution'
        ];

        // Ensure we send strict JSON framing manually so the Python server parses it
        $I->haveHttpHeader('Content-Type', 'application/json');
        $I->sendPost('/job/complete', json_encode($payload));

        // Confirm the server accepted the job completion successfully
        $I->seeResponseCodeIs(200);

        // Introduce a microscopic wait incase underlying IO delays
        usleep(500000);

        // Set filesystem paths to test against the results
        $runDir = __DIR__ . '/../../runs/codeception_test_1';
        $extractedDir = $runDir . '/extracted';

        // Assert the standard raw output actually wrote
        $I->assertTrue(file_exists($runDir . '/response.txt'), 'Response text was not generated');
        
        // Assert the snippet parser recognized and output the JS snippet
        $I->assertTrue(file_exists($extractedDir . '/app.js'), 'app.js snippet was not extracted');
        
        // Assert the snippet parser generated a valid fallback extraction
        $I->assertTrue(file_exists($extractedDir . '/snippet_02.css'), 'Fallback CSS snippet was not extracted');
        
        // Assert the metadata tracker JSON was placed properly
        $I->assertTrue(file_exists($runDir . '/extracted_files.json'), 'extracted_files.json manifest is missing');
    }
}

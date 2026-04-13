# Power Automate Desktop Flow Blueprint

## Flow Name
AxureRunner

## Inputs
- action (Text)
- payloadJson (Text)
- token (Text)

## Output
Set flow output variable named resultJson (Text) in this schema:

{
  "ok": true,
  "action": "add_page",
  "message": "Page created",
  "outputPath": null,
  "details": {}
}

On failure:

{
  "ok": false,
  "action": "add_page",
  "message": "Reason",
  "outputPath": null,
  "details": { "errorCode": "AXURE_UI_TIMEOUT" }
}

## Global Variables
- axureWindowTitle = "Axure RP"
- maxRetries = 3
- retryDelayMs = 700

## Common Prologue (every action)
1. If token is empty, return failure.
2. Launch or attach Axure RP window.
3. Wait for window "Axure RP" exists (timeout 20s).
4. Activate Axure window.
5. Parse payloadJson into object payload.

## Switch(action)

### Case: open_project
Expected payload:
{
  "projectPath": "C:\\path\\to\\project.rp"
}

PAD Steps:
1. Send keys Ctrl+O
2. Wait for Open dialog
3. Populate file path field with payload.projectPath
4. Press Enter
5. Wait until project title reflects opened file (or editor ready)
6. Set resultJson success

### Case: add_page
Expected payload:
{
  "pageName": "Dashboard",
  "parentPage": "Home"
}

PAD Steps:
1. In sitemap pane, optionally locate parentPage
2. Open context menu New Child Page or New Page
3. Type payload.pageName
4. Confirm and wait for page appears in tree
5. Set resultJson success

### Case: add_text
Expected payload:
{
  "pageName": "Dashboard",
  "text": "Welcome",
  "x": 120,
  "y": 80,
  "w": 200,
  "h": 24
}

PAD Steps:
1. Navigate to pageName in sitemap
2. Insert Text widget from widget library
3. Place at x,y
4. Set size w,h
5. Set text
6. Set resultJson success

### Case: add_button
Expected payload:
{
  "pageName": "Dashboard",
  "label": "Save",
  "x": 120,
  "y": 140,
  "w": 96,
  "h": 32
}

PAD Steps:
1. Navigate to pageName
2. Insert Button widget
3. Place and resize
4. Set label
5. Set resultJson success

### Case: export_html
Expected payload:
{
  "outputFolder": "C:\\path\\to\\output",
  "openAfterExport": false
}

PAD Steps:
1. Send keys Ctrl+Shift+E (or use Publish menu)
2. Choose HTML output target folder
3. Disable openAfterExport if configured
4. Start export
5. Wait for completion signal/dialog
6. Set resultJson with outputPath = outputFolder

### Case: save_project
Expected payload:
{}

PAD Steps:
1. Send keys Ctrl+S
2. Wait for save completion
3. Set resultJson success

### Default
Return unsupported action error.

## Reliability Guidance
- Prefer UI elements selectors over coordinates.
- If selector fails, retry up to maxRetries.
- Use fixed zoom and workspace layout profile in Axure.
- Keep Axure on primary monitor during automation.

## Security Guidance
- Validate token in flow before any UI operation.
- Reject actions not in allowlist.
- Do not expose this flow remotely.

## Store Install Wrapper (Recommended for Your Setup)

Your installed PAD variant is from Microsoft Store, which usually does not expose PAD.Console.Host.exe. Use a cloud flow wrapper to trigger desktop flow AxureRunner.

### Cloud Flow Name
AxureRunnerBridge

### Trigger
When an HTTP request is received

### Expected Request Body
{
  "token": "string",
  "flowName": "AxureRunner",
  "action": "add_page",
  "payload": {},
  "payloadJson": "{}"
}

### Steps
1. Validate token equals your shared secret; if not, return 401-style payload.
2. Run a desktop flow action targeting AxureRunner on your machine.
3. Map desktop flow input variables:
   - action <- triggerBody().action
   - payloadJson <- triggerBody().payloadJson
   - token <- triggerBody().token
4. Return JSON response from desktop flow output resultJson.

### Response Example
{
  "ok": true,
  "action": "export_html",
  "message": "Export complete",
  "outputPath": "C:\\AxureOut",
  "details": {}
}

### Local Configuration
Set environment variable PAD_RUN_URL to the cloud flow HTTP URL so run-pad-action.ps1 can invoke it.

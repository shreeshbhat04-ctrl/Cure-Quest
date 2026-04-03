def render_dashboard() -> str:
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Cure-Quest Demo</title>
        <style>
          :root {
            color-scheme: light;
            --bg: #f2efe8;
            --card: #fffaf2;
            --ink: #1f2a2e;
            --accent: #156f63;
            --muted: #6d7778;
            --border: #d9d2c5;
          }
          body {
            margin: 0;
            font-family: Georgia, "Times New Roman", serif;
            background: radial-gradient(circle at top, #fffdf8, var(--bg));
            color: var(--ink);
          }
          main {
            max-width: 900px;
            margin: 0 auto;
            padding: 48px 20px 72px;
          }
          .hero, .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 12px 40px rgba(31, 42, 46, 0.06);
          }
          .hero {
            margin-bottom: 18px;
          }
          h1, h2 {
            margin-top: 0;
          }
          code {
            background: #f1ebdf;
            padding: 2px 6px;
            border-radius: 6px;
          }
          ul {
            line-height: 1.6;
          }
          .muted {
            color: var(--muted);
          }
        </style>
      </head>
      <body>
        <main>
          <section class="hero">
            <p class="muted">Cure-Quest V1 bootstrap</p>
            <h1>FastAPI, MCP, and Google ADK are scaffolded.</h1>
            <p>Use the API endpoints for workflow testing, <code>/demo</code> for this dashboard, and the scripts folder for MCP and ADK smoke tests.</p>
          </section>
          <section class="card">
            <h2>Starter endpoints</h2>
            <ul>
              <li><code>GET /health</code></li>
              <li><code>GET /demo</code></li>
              <li><code>POST /patient/intake</code></li>
              <li><code>POST /prescription/scan</code></li>
              <li><code>POST /patient/check-alternatives</code></li>
              <li><code>POST /patient/escalate</code></li>
              <li><code>POST /patient/notify</code></li>
              <li><code>GET /cases/{case_id}</code></li>
            </ul>
          </section>
        </main>
      </body>
    </html>
    """

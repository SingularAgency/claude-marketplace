# HTML Report Template

Use this template structure to generate the Trustworthiness Report HTML file. Replace all placeholder values (wrapped in `{{ }}`) with actual data. The file must be fully self-contained with no external dependencies.

## Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Trustworthiness Report — {{ TALENT_NAME }} — {{ MONTH }} {{ YEAR }}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      color: #1a1a1a;
      background: #f8f9fa;
      line-height: 1.6;
      padding: 2rem;
    }

    .container {
      max-width: 800px;
      margin: 0 auto;
      background: #ffffff;
      border-radius: 12px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
      overflow: hidden;
    }

    .header {
      background: #1a1a2e;
      color: #ffffff;
      padding: 2.5rem 2.5rem 2rem;
    }

    .header h1 {
      font-size: 1.5rem;
      font-weight: 600;
      margin-bottom: 0.25rem;
    }

    .header .subtitle {
      font-size: 0.95rem;
      color: #a0a0b8;
      font-weight: 400;
    }

    .header .meta {
      margin-top: 1rem;
      font-size: 0.85rem;
      color: #a0a0b8;
    }

    .warning-banner {
      background: #fff3cd;
      border-left: 4px solid #ffc107;
      color: #856404;
      padding: 1rem 2.5rem;
      font-size: 0.9rem;
    }

    .body {
      padding: 2.5rem;
    }

    .section-title {
      font-size: 1.1rem;
      font-weight: 600;
      color: #1a1a2e;
      margin-bottom: 1.25rem;
      padding-bottom: 0.5rem;
      border-bottom: 2px solid #eef0f2;
    }

    .criteria-card {
      margin-bottom: 1.75rem;
      padding: 1.25rem 1.5rem;
      border-radius: 8px;
      background: #fafbfc;
      border: 1px solid #eef0f2;
    }

    .criteria-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
    }

    .criteria-name {
      font-size: 1rem;
      font-weight: 600;
      color: #1a1a2e;
    }

    .score-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 48px;
      height: 48px;
      border-radius: 50%;
      font-size: 1.1rem;
      font-weight: 700;
      color: #ffffff;
    }

    .score-excellent { background: #28a745; }
    .score-strong    { background: #17a2b8; }
    .score-adequate  { background: #ffc107; color: #1a1a1a; }
    .score-developing { background: #fd7e14; }
    .score-poor      { background: #dc3545; }

    .score-bar-container {
      width: 100%;
      height: 6px;
      background: #e9ecef;
      border-radius: 3px;
      margin-bottom: 0.75rem;
      overflow: hidden;
    }

    .score-bar {
      height: 100%;
      border-radius: 3px;
      transition: width 0.3s ease;
    }

    .justification {
      font-size: 0.9rem;
      color: #4a4a5a;
      line-height: 1.65;
    }

    .overall-section {
      margin-top: 2rem;
      padding: 1.5rem;
      background: #f0f4ff;
      border-radius: 8px;
      border: 1px solid #d0daf0;
    }

    .overall-section h3 {
      font-size: 1rem;
      font-weight: 600;
      color: #1a1a2e;
      margin-bottom: 0.75rem;
    }

    .overall-section p {
      font-size: 0.9rem;
      color: #4a4a5a;
      line-height: 1.7;
    }

    .summary-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 0.75rem;
      margin-bottom: 2rem;
    }

    .summary-cell {
      text-align: center;
      padding: 1rem 0.5rem;
      background: #fafbfc;
      border-radius: 8px;
      border: 1px solid #eef0f2;
    }

    .summary-cell .label {
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #6c757d;
      margin-bottom: 0.35rem;
    }

    .summary-cell .value {
      font-size: 1.4rem;
      font-weight: 700;
    }

    .footer {
      text-align: center;
      padding: 1.5rem 2.5rem;
      font-size: 0.8rem;
      color: #adb5bd;
      border-top: 1px solid #eef0f2;
    }

    .transcript-count {
      display: inline-block;
      background: #e9ecef;
      color: #495057;
      padding: 0.2rem 0.6rem;
      border-radius: 4px;
      font-size: 0.85rem;
      margin-left: 0.5rem;
    }
  </style>
</head>
<body>
  <div class="container">

    <div class="header">
      <h1>Trustworthiness Report</h1>
      <div class="subtitle">{{ TALENT_NAME }}</div>
      <div class="meta">
        {{ MONTH }} {{ YEAR }} · <span class="transcript-count">{{ TRANSCRIPT_COUNT }} transcripts analyzed</span>
      </div>
    </div>

    <!-- ONLY include this block if fewer than 3 transcripts were found -->
    <div class="warning-banner">
      ⚠ Insufficient transcript data: only {{ TRANSCRIPT_COUNT }} transcript(s) found for this period. Scores may not fully reflect this person's typical behavior. Consider re-evaluating with more data.
    </div>

    <div class="body">

      <h2 class="section-title">Score Overview</h2>

      <div class="summary-grid">
        <!-- Repeat for each criterion. Use the appropriate color class:
             score-excellent (9-10), score-strong (7-8), score-adequate (5-6),
             score-developing (3-4), score-poor (1-2) -->
        <div class="summary-cell">
          <div class="label">Credibility</div>
          <div class="value" style="color: {{ COLOR }}">{{ SCORE }}/10</div>
        </div>
        <div class="summary-cell">
          <div class="label">Reliability</div>
          <div class="value" style="color: {{ COLOR }}">{{ SCORE }}/10</div>
        </div>
        <div class="summary-cell">
          <div class="label">Intimacy</div>
          <div class="value" style="color: {{ COLOR }}">{{ SCORE }}/10</div>
        </div>
        <div class="summary-cell">
          <div class="label">Group Think</div>
          <div class="value" style="color: {{ COLOR }}">{{ SCORE }}/10</div>
        </div>
        <div class="summary-cell">
          <div class="label">English</div>
          <div class="value" style="color: {{ COLOR }}">{{ SCORE }}/10</div>
        </div>
      </div>

      <h2 class="section-title">Detailed Evaluation</h2>

      <!-- Repeat this card block for each of the 5 criteria -->
      <div class="criteria-card">
        <div class="criteria-header">
          <span class="criteria-name">{{ CRITERION_NAME }}</span>
          <span class="score-badge {{ SCORE_CLASS }}">{{ SCORE }}</span>
        </div>
        <div class="score-bar-container">
          <div class="score-bar {{ SCORE_CLASS }}" style="width: {{ SCORE * 10 }}%; background: {{ BAR_COLOR }};"></div>
        </div>
        <div class="justification">
          {{ JUSTIFICATION_TEXT }}
        </div>
      </div>
      <!-- End repeat -->

      <div class="overall-section">
        <h3>Overall Feedback</h3>
        <p>{{ OVERALL_FEEDBACK_PARAGRAPH }}</p>
      </div>

    </div>

    <div class="footer">
      Generated on {{ GENERATION_DATE }} · Trustworthiness Report Plugin · Singular Agency
    </div>

  </div>
</body>
</html>
```

## Color Mapping

Use these colors for score values and bar fills:

| Score Range | Class              | Badge Color | Bar/Text Color |
|-------------|--------------------|-------------|----------------|
| 9–10        | `score-excellent`  | `#28a745`   | `#28a745`      |
| 7–8         | `score-strong`     | `#17a2b8`   | `#17a2b8`      |
| 5–6         | `score-adequate`   | `#ffc107`   | `#c89e00`      |
| 3–4         | `score-developing` | `#fd7e14`   | `#fd7e14`      |
| 1–2         | `score-poor`       | `#dc3545`   | `#dc3545`      |

## Rendering Rules

1. **Warning banner**: Only include the `.warning-banner` div if `TRANSCRIPT_COUNT < 3`. Remove it entirely otherwise.
2. **Score badge class**: Map the numeric score to the appropriate class using the table above.
3. **Score bar width**: Calculate as `score * 10` percent.
4. **Summary grid colors**: Use the "Bar/Text Color" from the table for the `.value` font color.
5. **Generation date**: Use the current date in "March 27, 2026" format.
6. **All CSS must remain in the `<style>` block** — no external stylesheets.
7. **Do not include any JavaScript** — the report is a static document.

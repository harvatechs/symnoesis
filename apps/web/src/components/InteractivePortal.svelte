<script lang="ts">
  import { onMount } from "svelte";

  // Stepper state
  let currentStep = 1; // 1: Intro, 2: Domain/Context, 3: Questions, 4: Results
  let questionCluster = 1; // 1: Agency (H1), 2: Capability (H2), 3: Epistemic (H3), 4: Wellbeing (H4)

  // Domain selection
  let selectedDomain = "learning";

  // Responses (1-5 scale, 0 for "Prefer not to say")
  let answers = {
    // Agency (H1)
    q1_override: 3,
    q2_formulate: 3,
    // Capability (H2)
    q3_unaided: 3,
    q4_practice: 3,
    // Epistemic (H3)
    q5_verify: 3,
    q6_disagree: 3,
    // Wellbeing (H4)
    q7_distress: 3,
    q8_reliance: 3,
  };

  // Results calculation
  let modalPixel = "h1011-m0110";
  let zoneName = "Zone 2 (Productive)";
  let estimatedSQ = 28.7;
  let singleFlipExperiment = "Schedule one 30-minute practice session per week solving core problems unaided before prompting the system.";

  function nextStep() {
    if (currentStep === 3) {
      if (questionCluster < 4) {
        questionCluster += 1;
        return;
      }
    }
    currentStep += 1;
    if (currentStep === 4) {
      calculateResult();
    }
  }

  function prevStep() {
    if (currentStep === 3 && questionCluster > 1) {
      questionCluster -= 1;
      return;
    }
    currentStep -= 1;
  }

  function calculateResult() {
    // Deterministic projection based on self-reported answers
    const h1 = (answers.q1_override + answers.q2_formulate) / 2 >= 3 ? "1" : "0";
    const h2 = (answers.q3_unaided + answers.q4_practice) / 2 >= 3 ? "1" : "0";
    const h3 = (answers.q5_verify + answers.q6_disagree) / 2 >= 3 ? "1" : "0";
    const h4 = (answers.q7_distress + answers.q8_reliance) / 2 <= 3 ? "1" : "0";

    const hBits = `${h1}${h2}${h3}${h4}`;
    modalPixel = `h${hBits}-m0110`;

    if (h1 === "1" && h2 === "1" && h3 === "1" && h4 === "1") {
      zoneName = "Zone 1 (Mutualistic)";
      estimatedSQ = 68.4;
      singleFlipExperiment = "Maintain deliberate unaided skill checks to monitor retention over long projects.";
    } else if (h2 === "0") {
      zoneName = "Zone 4 (Watch)";
      estimatedSQ = -12.3;
      singleFlipExperiment = "Variable H2 (capability trajectory) is your highest-leverage dimension. Test solving the initial phase of tasks without consulting the model.";
    } else if (h1 === "0" && h4 === "0") {
      zoneName = "Zone 5 (Dependence)";
      estimatedSQ = -42.8;
      singleFlipExperiment = "Re-establish active decision boundaries: explicitly write down your acceptance criteria before prompting the model.";
    } else {
      zoneName = "Zone 2 (Productive)";
      estimatedSQ = 31.5;
      singleFlipExperiment = "Increase verification frequency (H3): deliberately test critical model assertions against authoritative documentation.";
    }
  }

  function restart() {
    currentStep = 1;
    questionCluster = 1;
  }
</script>

<div class="portal-container">
  <!-- Privacy & Evidence Banner (Permanent) -->
  <div class="portal-banner">
    <div class="banner-badge">
      <span class="badge-tier e0">UNCALIBRATED PROTOTYPE E0</span>
    </div>
    <p class="banner-text">
      Weights come from expert judgment and have not been validated against empirical outcome data. 
      <strong>Zero data leaves your browser.</strong> Your answers are never stored or transmitted over any network.
    </p>
  </div>

  {#if currentStep === 1}
    <!-- Screen 1: Intro -->
    <div class="screen-card">
      <h2>Interactive Self-Assessment Portal</h2>
      <p class="lead">
        This self-assessment projects your habits onto the Symnoesis Map. It provides a descriptive, non-diagnostic estimate of your dyadic pattern.
      </p>
      <div class="info-list">
        <div class="info-item">
          <strong>Time Required:</strong> ~3 minutes (8 items).
        </div>
        <div class="info-item">
          <strong>Privacy Guarantee:</strong> Pure client-side computation. No cookies, no accounts, no server logging.
        </div>
        <div class="info-item">
          <strong>Non-Diagnostic:</strong> Does not assess medical, psychiatric, or mental health status.
        </div>
      </div>
      <div class="actions">
        <button type="button" class="btn btn-primary" on:click={nextStep}>Start Assessment</button>
      </div>
    </div>

  {:else if currentStep === 2}
    <!-- Screen 2: Context / Domain -->
    <div class="screen-card">
      <span class="step-indicator">Step 1 of 3: Usage Context</span>
      <h2>Your Primary Use Case</h2>
      <p class="form-help">Select the domain where you spend the most active collaborative time with AI systems:</p>

      <div class="domain-grid">
        <label class="domain-choice" class:selected={selectedDomain === "learning"}>
          <input type="radio" name="domain" value="learning" bind:group={selectedDomain} />
          <div>
            <strong>Learning & Education</strong>
            <p>Studying concepts, academic writing, language practice, conceptual explanation.</p>
          </div>
        </label>
        <label class="domain-choice" class:selected={selectedDomain === "coding"}>
          <input type="radio" name="domain" value="coding" bind:group={selectedDomain} />
          <div>
            <strong>Software Engineering</strong>
            <p>Code generation, architecture design, debugging, refactoring, CLI workflows.</p>
          </div>
        </label>
        <label class="domain-choice" class:selected={selectedDomain === "health-information"}>
          <input type="radio" name="domain" value="health-information" bind:group={selectedDomain} />
          <div>
            <strong>Health Information</strong>
            <p>Symptom research, interpreting test reports, lifestyle and nutrition planning.</p>
          </div>
        </label>
        <label class="domain-choice" class:selected={selectedDomain === "advice-companionship"}>
          <input type="radio" name="domain" value="advice-companionship" bind:group={selectedDomain} />
          <div>
            <strong>Advice & Companionship</strong>
            <p>Personal reflection, decision support, conversational engagement.</p>
          </div>
        </label>
      </div>

      <div class="actions space-between">
        <button type="button" class="btn btn-secondary" on:click={prevStep}>Back</button>
        <button type="button" class="btn btn-primary" on:click={nextStep}>Next: Questions</button>
      </div>
    </div>

  {:else if currentStep === 3}
    <!-- Screen 3: Questions Clusters (4 Clusters) -->
    <div class="screen-card">
      <span class="step-indicator">Step 2 of 3 — Question Cluster {questionCluster} of 4</span>

      {#if questionCluster === 1}
        <h2>Agency & Task Direction (Variable H1)</h2>
        <div class="question-block">
          <label class="q-label" for="q1">1. When the AI proposes a solution or plan, how often do you actively critique or override it?</label>
          <select id="q1" class="scale-select" bind:value={answers.q1_override}>
            <option value={1}>1 — Rarely or never; I accept defaults</option>
            <option value={2}>2 — Occasionally on minor points</option>
            <option value={3}>3 — Moderate; about half the time</option>
            <option value={4}>4 — Frequently; I rigorously inspect each output</option>
            <option value={5}>5 — Always; I direct and heavily modify the output</option>
            <option value={0}>0 — Prefer not to say</option>
          </select>
        </div>

        <div class="question-block">
          <label class="q-label" for="q2">2. Who initiates and formulates the core direction of the work?</label>
          <select id="q2" class="scale-select" bind:value={answers.q2_formulate}>
            <option value={1}>1 — The system prompts and guides my workflow entirely</option>
            <option value={2}>2 — Mostly the system; I react to suggestions</option>
            <option value={3}>3 — Shared balanced co-direction</option>
            <option value={4}>4 — Mostly me; the system acts as an implementer</option>
            <option value={5}>5 — Fully me; I set rigid requirements and milestones</option>
            <option value={0}>0 — Prefer not to say</option>
          </select>
        </div>

      {:else if questionCluster === 2}
        <h2>Capability Trajectory (Variable H2)</h2>
        <div class="question-block">
          <label class="q-label" for="q3">3. If the AI system were permanently unavailable, could you complete this task unaided?</label>
          <select id="q3" class="scale-select" bind:value={answers.q3_unaided}>
            <option value={1}>1 — No, I have lost the underlying knowledge/skill</option>
            <option value={2}>2 — Only with extreme difficulty and major delay</option>
            <option value={3}>3 — Yes, but noticeably slower</option>
            <option value={4}>4 — Yes, with solid competence and standard pace</option>
            <option value={5}>5 — Completely; my independent capability has grown</option>
            <option value={0}>0 — Prefer not to say</option>
          </select>
        </div>

        <div class="question-block">
          <label class="q-label" for="q4">4. When did you last perform a significant task in this domain completely unaided?</label>
          <select id="q4" class="scale-select" bind:value={answers.q4_practice}>
            <option value={1}>1 — More than 6 months ago</option>
            <option value={2}>2 — Within the last month</option>
            <option value={3}>3 — Within the last 2 weeks</option>
            <option value={4}>4 — Within the last week</option>
            <option value={5}>5 — Today or yesterday</option>
            <option value={0}>0 — Prefer not to say</option>
          </select>
        </div>

      {:else if questionCluster === 3}
        <h2>Epistemic Calibration (Variable H3)</h2>
        <div class="question-block">
          <label class="q-label" for="q5">5. When the AI delivers an authoritative response, how often do you cross-check primary sources?</label>
          <select id="q5" class="scale-select" bind:value={answers.q5_verify}>
            <option value={1}>1 — Never; I assume it is accurate</option>
            <option value={2}>2 — Only when something looks obviously wrong</option>
            <option value={3}>3 — Sometimes on critical details</option>
            <option value={4}>4 — Regularly check key facts and claims</option>
            <option value={5}>5 — Always verify against primary documentation</option>
            <option value={0}>0 — Prefer not to say</option>
          </select>
        </div>

        <div class="question-block">
          <label class="q-label" for="q6">6. Do you intentionally prompt or seek disagreement to test the bounds of the system?</label>
          <select id="q6" class="scale-select" bind:value={answers.q6_disagree}>
            <option value={1}>1 — Never; I seek direct answers</option>
            <option value={2}>2 — Rarely</option>
            <option value={3}>3 — Occasionally</option>
            <option value={4}>4 — Frequently test edge cases and logic</option>
            <option value={5}>5 — Standard practice in all sessions</option>
            <option value={0}>0 — Prefer not to say</option>
          </select>
        </div>

      {:else}
        <h2>Wellbeing & Sustainable Reliance (Variable H4)</h2>
        <div class="question-block">
          <label class="q-label" for="q7">7. Do you experience discomfort or paralysis when required to work without the AI?</label>
          <select id="q7" class="scale-select" bind:value={answers.q7_distress}>
            <option value={5}>5 — Severe anxiety or total procrastination</option>
            <option value={4}>4 — Noticeable frustration and reluctance</option>
            <option value={3}>3 — Mild inconvenience</option>
            <option value={2}>2 — Minimal; comfortable working offline</option>
            <option value={1}>1 — None; I enjoy working independently</option>
            <option value={0}>0 — Prefer not to say</option>
          </select>
        </div>

        <div class="question-block">
          <label class="q-label" for="q8">8. To what degree does interaction with the system substitute for human peer feedback?</label>
          <select id="q8" class="scale-select" bind:value={answers.q8_reliance}>
            <option value={5}>5 — Total replacement; I rarely consult colleagues</option>
            <option value={4}>4 — Heavy substitution; colleagues are secondary</option>
            <option value={3}>3 — Moderate; balanced with peers</option>
            <option value={2}>2 — Minimal; system is a preliminary draft tool</option>
            <option value={1}>1 — None; strong human collaboration remains primary</option>
            <option value={0}>0 — Prefer not to say</option>
          </select>
        </div>
      {/if}

      <div class="actions space-between">
        <button type="button" class="btn btn-secondary" on:click={prevStep}>Back</button>
        <button type="button" class="btn btn-primary" on:click={nextStep}>
          {questionCluster === 4 ? "View Results" : "Next Cluster"}
        </button>
      </div>
    </div>

  {:else}
    <!-- Screen 4: Results View per 07_UX_RULES §6.1 -->
    <div class="screen-card result-screen">
      <span class="step-indicator">Step 3 of 3: Descriptive Projection</span>
      <h2>Where your answers place you on the map</h2>

      <div class="result-summary-box">
        <p class="result-lead">
          Based on your answers, the most likely projected state is <code>{modalPixel}</code>, situated in <strong>{zoneName}</strong>. 
          This is an estimate from self-reported habits, not an objective clinical measurement.
        </p>
        <div class="stat-row">
          <div class="stat-item">
            <span class="stat-label">Projected SQ:</span>
            <span class="stat-value">{estimatedSQ > 0 ? "+" : ""}{estimatedSQ}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Governance Zone:</span>
            <span class="stat-value">{zoneName.split(" ")[0]}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Evidence Tier:</span>
            <span class="badge-tier e0">E0 EXPERT SPEC</span>
          </div>
        </div>
      </div>

      <div class="suggestions-section">
        <h3>Single-Flip Diagnostic Experiment</h3>
        <p>
          Under the SYMN-01 framework, improvement is evaluated as single-variable counterfactual steps rather than sweeping behavior overhauls:
        </p>
        <div class="academic-callout info">
          <strong>Recommended Experiment:</strong><br />
          {singleFlipExperiment}
        </div>
      </div>

      <div class="limitations-section">
        <h3>What this does not show</h3>
        <ul>
          <li><strong>Self-report bias:</strong> Answers reflect subjective perception rather than passive behavioral telemetry.</li>
          <li><strong>Uncalibrated weights:</strong> The underlying projection model uses expert-elicited E0 weights pending empirical calibration.</li>
          <li><strong>No causal claim:</strong> Sitting in a given zone does not prove the AI system caused the outcome.</li>
        </ul>
      </div>

      <div class="support-line">
        <p>
          If you are experiencing distress or compulsive reliance, you can talk to a professional or find a confidential local helpline at 
          <a href="https://findahelpline.com" target="_blank" rel="noopener noreferrer">findahelpline.com</a>.
        </p>
      </div>

      <div class="actions">
        <button type="button" class="btn btn-secondary" on:click={restart}>Start Over</button>
        <a href={`${import.meta.env.BASE_URL.replace(/\/$/, "")}/map`} class="btn btn-primary">Locate {modalPixel} on the Map</a>
      </div>
    </div>
  {/if}
</div>

<style>
  .portal-container {
    max-width: 720px;
    margin: 2rem auto;
    padding: 0 1rem;
  }

  .portal-banner {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius-md);
    padding: 1rem 1.25rem;
    margin-bottom: 2rem;
  }

  .banner-badge {
    margin-bottom: 0.5rem;
  }

  .banner-text {
    font-size: var(--text-small);
    color: var(--ink-2);
    margin: 0;
    line-height: 1.5;
  }

  .screen-card {
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: var(--radius-md);
    padding: 2rem;
  }

  .step-indicator {
    font-size: var(--text-caption);
    font-family: var(--font-mono);
    color: var(--ink-3);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: block;
    margin-bottom: 0.5rem;
  }

  .screen-card h2 {
    font-size: var(--text-h2);
    font-weight: 600;
    margin: 0 0 1rem 0;
    color: var(--ink);
  }

  .screen-card .lead {
    font-size: 1.125rem;
    color: var(--ink-2);
    margin: 0 0 1.5rem 0;
    line-height: 1.5;
  }

  .info-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-bottom: 2rem;
    font-size: 0.9375rem;
    color: var(--ink-2);
  }

  .info-item {
    background: var(--surface);
    padding: 0.75rem 1rem;
    border-radius: var(--radius-sm);
    border: 1px solid var(--line);
  }

  .form-help {
    font-size: 0.9375rem;
    color: var(--ink-3);
    margin-bottom: 1.25rem;
  }

  .domain-grid {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-bottom: 2rem;
  }

  .domain-choice {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 1rem;
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
    cursor: pointer;
    background: var(--paper);
    transition: border-color 0.15s ease;
  }

  .domain-choice:hover {
    border-color: var(--line-strong);
  }

  .domain-choice.selected {
    border-color: var(--ink);
    background: var(--surface);
  }

  .domain-choice p {
    margin: 0.25rem 0 0 0;
    font-size: var(--text-small);
    color: var(--ink-3);
  }

  .question-block {
    margin-bottom: 1.75rem;
  }

  .q-label {
    display: block;
    font-size: 1rem;
    font-weight: 500;
    color: var(--ink);
    margin-bottom: 0.5rem;
  }

  .scale-select {
    width: 100%;
    padding: 0.65rem 0.75rem;
    border-radius: var(--radius-sm);
    border: 1px solid var(--line-strong);
    background: var(--paper);
    color: var(--ink);
    font-size: 0.9375rem;
  }

  .actions {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
  }

  .actions.space-between {
    justify-content: space-between;
  }

  .btn {
    padding: 0.65rem 1.25rem;
    border-radius: var(--radius-sm);
    font-size: 0.9375rem;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
  }

  .btn-primary {
    background: var(--ink);
    color: var(--paper);
    border: 1px solid var(--ink);
  }

  .btn-secondary {
    background: var(--surface);
    color: var(--ink);
    border: 1px solid var(--line-strong);
  }

  .result-summary-box {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
    padding: 1.5rem;
    margin: 1.5rem 0;
  }

  .result-lead {
    font-size: 1.0625rem;
    line-height: 1.6;
    margin: 0 0 1.25rem 0;
  }

  .stat-row {
    display: flex;
    gap: 2rem;
    border-top: 1px solid var(--line);
    padding-top: 1rem;
    flex-wrap: wrap;
  }

  .stat-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .stat-label {
    font-size: var(--text-caption);
    color: var(--ink-3);
  }

  .stat-value {
    font-size: 1.25rem;
    font-weight: 600;
    font-family: var(--font-mono);
  }

  .suggestions-section, .limitations-section {
    margin: 2rem 0;
  }

  .suggestions-section h3, .limitations-section h3 {
    font-size: 1.125rem;
    font-weight: 600;
    margin: 0 0 0.75rem 0;
  }

  .limitations-section ul {
    padding-left: 1.25rem;
    font-size: 0.9375rem;
    color: var(--ink-2);
  }

  .limitations-section li {
    margin-bottom: 0.5rem;
  }

  .support-line {
    background: var(--surface-alt);
    padding: 0.75rem 1rem;
    border-radius: var(--radius-sm);
    font-size: var(--text-caption);
    color: var(--ink-2);
    margin: 1.5rem 0;
  }

  .support-line p {
    margin: 0;
  }
</style>

// Node worker for TypeScript solveMfc MILP set cover testing
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  const coverModule = await import('../packages/ts/dist/cover.js');
  const { solveMfc, DEFAULT_COVER_CONFIG } = coverModule;

  const inputJsonPath = process.argv[2];
  const outputJsonPath = process.argv[3];

  if (!inputJsonPath || !outputJsonPath) {
    console.error('Usage: node challenger_m2_milp_worker.js <input.json> <output.json>');
    process.exit(1);
  }

  const raw = fs.readFileSync(inputJsonPath, 'utf-8');
  const scenarios = JSON.parse(raw);

  const results = [];
  for (const sc of scenarios) {
    const id = sc.id;
    const cells = sc.cells;

    try {
      const res = solveMfc(cells);
      results.push({
        id,
        success: true,
        solver_status: res.solver_status,
        total_harm_mass: res.total_harm_mass,
        covered_harm_mass: res.covered_harm_mass,
        total_coverage: res.total_coverage,
        rules_count: res.rules.length,
        rules: res.rules.map(r => ({
          rule_str: r.rule_str,
          literals: r.literals,
          purity: r.purity,
          coverage: r.coverage,
          harm_mass_covered: r.harm_mass_covered,
          n_eff: r.n_eff,
          unobserved_covered: r.unobserved_covered
        }))
      });
    } catch (err) {
      results.push({
        id,
        success: false,
        error: String(err)
      });
    }
  }

  fs.writeFileSync(outputJsonPath, JSON.stringify(results, null, 2), 'utf-8');
  console.log(`TypeScript solveMfc worker processed ${results.length} scenarios.`);
}

main().catch(err => {
  console.error('Fatal worker error:', err);
  process.exit(1);
});

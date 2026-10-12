// Worker to compute TypeScript Quine-McCluskey for batch test cases
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  const coverModule = await import('../packages/ts/dist/cover.js');
  const { quineMccluskeyBoolean, quineMccluskey } = coverModule;

  const inputJsonPath = process.argv[2];
  const outputJsonPath = process.argv[3];

  if (!inputJsonPath || !outputJsonPath) {
    console.error('Usage: node challenger_m2_qm_worker.js <input.json> <output.json>');
    process.exit(1);
  }

  const raw = fs.readFileSync(inputJsonPath, 'utf-8');
  const testCases = JSON.parse(raw);

  const results = [];
  for (const tc of testCases) {
    const minterms = tc.minterms;
    const dontcares = tc.dontcares || [];
    const variables = tc.variables;

    try {
      const boolExpr = quineMccluskeyBoolean(minterms, dontcares, variables);
      const rules = quineMccluskey(minterms, dontcares, variables);
      results.push({
        id: tc.id,
        success: true,
        boolExpr,
        rulesCount: rules.length,
        rules: rules.map(r => ({ rule_str: r.rule_str, literals: r.literals, purity: r.purity, coverage: r.coverage }))
      });
    } catch (err) {
      results.push({
        id: tc.id,
        success: false,
        error: String(err)
      });
    }
  }

  fs.writeFileSync(outputJsonPath, JSON.stringify(results, null, 2), 'utf-8');
  console.log(`Successfully processed ${results.length} test cases in TypeScript.`);
}

main().catch(err => {
  console.error('Fatal worker error:', err);
  process.exit(1);
});

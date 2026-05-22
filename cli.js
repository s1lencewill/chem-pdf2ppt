#!/usr/bin/env node
/**
 * PDF2PPT CLI — Cross-platform entry point
 */
const path = require('path');
const { execSync } = require('child_process');

const SKILL_ROOT = __dirname;
const cmd = process.argv[2];
const args = process.argv.slice(3);

function run(scriptName, extraArgs = []) {
  const scriptPath = path.join(SKILL_ROOT, 'scripts', scriptName);
  const allArgs = [...extraArgs, ...args];
  const quoted = allArgs.map(a => `"${a}"`).join(' ');
  try {
    execSync(`python "${scriptPath}" ${quoted}`, { stdio: 'inherit' });
  } catch (e) {
    process.exit(1);
  }
}

const help = `
chem-pdf2ppt v2.0 — Chemistry Academic Paper to PPT/HTML Converter

Commands:
  analyze <paper.pdf> [--json report.json]   Analyze paper structure and type
  extract <paper.pdf> <output_dir> [dpi] [--report]   Extract figures from PDF
  help                                       Show this help

Examples:
  chem-pdf2ppt analyze paper.pdf --json analysis.json
  chem-pdf2ppt extract paper.pdf figures/ 300 --report

For building PPT/HTML presentations, use the Python API directly:
  from create_ppt import ChemistryPPT
  from generate_html import HtmlPPT

Full docs: https://github.com/s1lencewill/chem-pdf2ppt
`;

switch (cmd) {
  case 'analyze':
    run('analyze_paper.py');
    break;
  case 'extract':
    run('extract_charts.py');
    break;
  case 'help':
  case '--help':
  case '-h':
    console.log(help);
    break;
  default:
    console.log(help);
    break;
}

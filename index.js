#!/usr/bin/env node
/**
 * PDF2PPT — Chemistry Academic Paper to Presentation Converter
 *
 * Usage (Python API via require):
 *   const { analyze, extract, createPPT, createHTML } = require('pdf2ppt');
 *
 * CLI:
 *   npm install -g pdf2ppt
 *   pdf2ppt-analyze paper.pdf
 *   pdf2ppt-extract paper.pdf figures/ 300
 */

const path = require('path');
const { execSync } = require('child_process');
const fs = require('fs');

const SKILL_ROOT = __dirname;

function python(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf-8', stdio: 'pipe', cwd: SKILL_ROOT });
  } catch (e) {
    console.error('Python execution failed:', e.message);
    throw e;
  }
}

module.exports = {
  SKILL_ROOT,
  version: '2.0.0',

  /**
   * Analyze a chemistry paper PDF
   * @param {string} pdfPath - path to PDF file
   * @param {object} opts - { json?: boolean, outputPath?: string }
   * @returns {object} analysis result
   */
  analyze(pdfPath, opts = {}) {
    const args = [path.join(SKILL_ROOT, 'scripts', 'analyze_paper.py'), pdfPath];
    if (opts.json) {
      const outPath = opts.outputPath || pdfPath.replace('.pdf', '_analysis.json');
      args.push('--json', outPath);
    }
    const cmd = `python ${args.map(a => `"${a}"`).join(' ')}`;
    return python(cmd);
  },

  /**
   * Extract figures from a chemistry paper PDF
   * @param {string} pdfPath - path to PDF
   * @param {string} outputDir - output directory for figures
   * @param {number} dpi - resolution (default 200)
   * @param {object} opts - { report?: boolean }
   */
  extract(pdfPath, outputDir, dpi = 200, opts = {}) {
    const args = [path.join(SKILL_ROOT, 'scripts', 'extract_charts.py'), pdfPath, outputDir, String(dpi)];
    if (opts.report) args.push('--report');
    const cmd = `python ${args.map(a => `"${a}"`).join(' ')}`;
    return python(cmd);
  },

  /**
   * Build a PPTX presentation from slide data
   */
  async createPPT(config) {
    // For Node.js usage, write config to temp file and run Python
    const tmpDir = require('os').tmpdir();
    const configPath = path.join(tmpDir, `pdf2ppt-config-${Date.now()}.json`);
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

    const script = path.join(SKILL_ROOT, 'scripts', 'create_ppt.py');
    // User should use the Python API directly for complex PPT building
    const cmd = `python -c "
import sys; sys.path.insert(0, '${SKILL_ROOT}/scripts')
from create_ppt import ChemistryPPT
import json
with open('${configPath}') as f:
    cfg = json.load(f)
ppt = ChemistryPPT(theme=cfg.get('theme', 'academic'))
for slide in cfg['slides']:
    getattr(ppt, slide['method'])(**slide['args'])
ppt.save(cfg['output'])
"`;
    return python(cmd);
  },

  /**
   * Build an HTML presentation from slide data
   */
  async createHTML(config) {
    const tmpDir = require('os').tmpdir();
    const configPath = path.join(tmpDir, `pdf2ppt-html-config-${Date.now()}.json`);
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

    const cmd = `python -c "
import sys; sys.path.insert(0, '${SKILL_ROOT}/scripts')
from generate_html import HtmlPPT
import json
with open('${configPath}') as f:
    cfg = json.load(f)
html = HtmlPPT(title=cfg.get('title', 'Presentation'), theme=cfg.get('theme', 'molecular'))
for slide in cfg['slides']:
    getattr(html, slide['method'])(**slide['args'])
html.save(cfg['output'])
"`;
    return python(cmd);
  },
};

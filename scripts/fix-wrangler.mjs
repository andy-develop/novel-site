#!/usr/bin/env node
// Remove SESSION KV binding from wrangler.json — we don't use sessions
import { readFileSync, writeFileSync } from 'fs';
const path = 'dist/server/wrangler.json';
const cfg = JSON.parse(readFileSync(path, 'utf8'));
delete cfg.kv_namespaces;
if (cfg.previews) delete cfg.previews.kv_namespaces;
writeFileSync(path, JSON.stringify(cfg, null, 0));
console.log('Removed SESSION KV binding from wrangler.json');

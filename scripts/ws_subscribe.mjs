// Subscribe to the rippled ledger stream on the public testnet WS endpoint.
// Node 24 built-in WebSocket. Usage: node ws_subscribe.mjs <wss-url> <seconds> <out-jsonl>
import { writeFileSync, appendFileSync } from 'node:fs';
const [url, secs, out] = process.argv.slice(2);
const startedAt = new Date().toISOString();
const ws = new WebSocket(url);
let received = 0, closes = 0, firstTs = null, lastTs = null;
const log = (o) => { appendFileSync(out, JSON.stringify(o) + '\n'); };
ws.onopen = () => {
  log({event: 'open', url, at: new Date().toISOString()});
  ws.send(JSON.stringify({command: 'subscribe', streams: ['ledger']}));
};
ws.onmessage = (ev) => {
  const d = JSON.parse(ev.data);
  received++;
  if (d.type === 'ledgerClosed') {
    closes++;
    const t = Date.parse(d.ledger_time_iso || d.ledger_time);
    if (firstTs === null) firstTs = t;
    lastTs = t;
    log({event: 'ledgerClosed', ledger_index: d.ledger_index, ledger_hash: d.ledger_hash,
         ledger_time_iso: d.ledger_time_iso, validated_ledgers: d.validated_ledgers,
         txn_count: d.txn_count, fee_base: d.fee_base, at: new Date().toISOString()});
  } else {
    log({event: 'other', type: d.type, at: new Date().toISOString()});
  }
};
ws.onerror = (e) => log({event: 'error', message: String(e.message || e), at: new Date().toISOString()});
ws.onclose = (e) => {
  log({event: 'close', code: e.code, reason: e.reason, at: new Date().toISOString(),
       summary: {received, closes, firstTs, lastTs, startedAt}});
  process.exit(0);
};
setTimeout(() => { ws.close(); }, Number(secs) * 1000);
setTimeout(() => { log({event: 'timeout-kill', at: new Date().toISOString()}); process.exit(2); }, Number(secs) * 1000 + 15000);

/**
 * Inbox watcher for the "One job off your plate" challenge (Builder track, Day 4).
 *
 * Runs in your own Google account's Apps Script. It only READS Gmail. Every minute it looks for new
 * messages that match QUERY. When it finds any, it starts your Claude Code scheduled task through its
 * API trigger, passing the Gmail thread ids as text. Claude does the work; this script never does.
 *
 * Your fire URL and token live in Project Settings -> Script properties (FIRE_URL, FIRE_TOKEN),
 * never in this file. Anyone with the token can start your task, so treat it like a password.
 */

// Which emails count. Test the search in Gmail first. Exclude your own address so your replies don't fire it.
const QUERY = 'in:inbox newer_than:1d -from:me';
const LOOKBACK_MS = 60 * 60 * 1000; // re-check the last hour every minute, so a slow-to-index email isn't missed

/** Run once by hand: turns the watcher on (every minute). */
function setup() {
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('check').timeBased().everyMinutes(1).create();
  Logger.log('Watcher on. Checks every minute from now.');
}

/** Run once by hand: turns the watcher off. */
function stop() {
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
  Logger.log('Watcher off.');
}

/** Run by hand to test the connection: starts one DRY RUN of your task. */
function testFire() {
  Logger.log(fire_('DRY RUN test from the Apps Script watcher. Use since = 3 days ago.'));
}

function check() {
  const props = PropertiesService.getScriptProperties();
  if (!props.getProperty('FIRE_URL') || !props.getProperty('FIRE_TOKEN')) {
    Logger.log('Set FIRE_URL and FIRE_TOKEN in Script properties first.');
    return;
  }
  const seen = JSON.parse(props.getProperty('SEEN') || '{}');
  const now = Date.now();
  const since = now - LOOKBACK_MS;
  const threads = [];
  const newIds = [];

  GmailApp.search(QUERY, 0, 30).forEach(thread => {
    if (thread.getLastMessageDate().getTime() < since) return;
    const fresh = thread.getMessages().filter(m => m.getDate().getTime() >= since && !seen[m.getId()]);
    if (fresh.length) {
      threads.push(thread.getId());
      fresh.forEach(m => newIds.push(m.getId()));
    }
  });

  if (threads.length) {
    const result = fire_('New emails in Gmail threads: ' + threads.join(', '));
    if (!/^2\d\d /.test(result)) {
      Logger.log('Fire failed, will retry next minute: ' + result);
      return; // not marked as seen, so the next check tries again
    }
    Logger.log('Fired for ' + threads.join(', '));
  }
  newIds.forEach(id => { seen[id] = now; });
  Object.keys(seen).forEach(id => { if (seen[id] < now - 3 * LOOKBACK_MS) delete seen[id]; }); // keep it small
  props.setProperty('SEEN', JSON.stringify(seen));
}

function fire_(text) {
  const props = PropertiesService.getScriptProperties();
  const res = UrlFetchApp.fetch(props.getProperty('FIRE_URL'), {
    method: 'post',
    contentType: 'application/json',
    muteHttpExceptions: true,
    headers: {
      Authorization: 'Bearer ' + props.getProperty('FIRE_TOKEN'),
      'anthropic-beta': 'experimental-cc-routine-2026-04-01',
      'anthropic-version': '2023-06-01',
    },
    payload: JSON.stringify({ text }),
  });
  return res.getResponseCode() + ' ' + res.getContentText();
}

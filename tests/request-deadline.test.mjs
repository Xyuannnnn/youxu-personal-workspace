import test from 'node:test';
import assert from 'node:assert/strict';
import {withRequestDeadline} from '../src/request-deadline.mjs';
test('successful requests return normally',async()=>{
  assert.equal(await withRequestDeadline(async()=>42,100),42);
});
test('stalled session times out and cannot initiate a late write',async()=>{
  let release,writes=0;
  const session=new Promise(resolve=>release=resolve);
  await assert.rejects(withRequestDeadline(async signal=>{
    await session;signal.throwIfAborted();writes++;
  },10),/超时/);
  release();await new Promise(resolve=>setTimeout(resolve,5));
  assert.equal(writes,0);
});
test('network operation is aborted on deadline',async()=>{
  let signal;
  await assert.rejects(withRequestDeadline(s=>{signal=s;return new Promise(()=>{})},10),/超时/);
  assert.equal(signal.aborted,true);
});
test('failure does not block a subsequent request',async()=>{
  await assert.rejects(withRequestDeadline(async()=>{throw Error('offline')},100),/offline/);
  assert.equal(await withRequestDeadline(async()=>true,100),true);
});

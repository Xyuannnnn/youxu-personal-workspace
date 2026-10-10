import {test} from 'node:test';
import assert from 'node:assert/strict';
import {WorkspaceStore,emptyWorkspace} from '../src/workspace-store.mjs';

test('new accounts are empty, existing owner data loads',async()=>{
 const empty=new WorkspaceStore(async()=>[],'alice');assert.deepEqual(await empty.load(),emptyWorkspace());
 assert.equal(empty.version,null);
 const own=new WorkspaceStore(async(method,path)=>{assert.match(path,/owner_id=eq.alice/);return [{payload:{name:'Alice'},version:3}]},'alice');
 assert.deepEqual(await own.load(),{name:'Alice'});assert.equal(own.version,3);
});
test('concurrent writes retain version and dirty draft on conflict',async()=>{
 const calls=[];const s=new WorkspaceStore(async(method,path,body)=>{calls.push({method,path,body});return method==='GET'?[{payload:emptyWorkspace(),version:4}]:[]},'alice');
 await s.load();await assert.rejects(s.save({name:'draft'}),/另一台设备/);
 assert.equal(s.version,4);assert.equal(s.dirty,true);assert.match(calls[1].path,/version=eq.4/);assert.equal(calls[1].body.version,5);
});
test('acknowledged saves advance version; network failures stay dirty',async()=>{
 let fails=false;const s=new WorkspaceStore(async(method,path,body)=>{if(fails)throw Error('offline');return [{version:body.version}]},'alice');
 await s.save(emptyWorkspace());assert.equal(s.version,1);assert.equal(s.dirty,false);
 fails=true;await assert.rejects(s.save(emptyWorkspace()),/offline/);assert.equal(s.version,1);assert.equal(s.dirty,true);
});

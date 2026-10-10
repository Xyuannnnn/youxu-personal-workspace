export function emptyWorkspace() {
  return {name:'GradLife',user:'同学',avatar:'',dark:false,theme:'blue',tasks:[],habits:{},habitDefinitions:[],ideas:[],money:[],workouts:[],notes:[],goals:[],reviews:[],schedules:[],folders:[]};
}

export class WorkspaceStore {
  constructor(request, uid) { this.request=request; this.uid=uid; this.version=null; this.dirty=false; }
  async load() {
    const rows=await this.request('GET', `?owner_id=eq.${encodeURIComponent(this.uid)}&select=payload,version`);
    if(!Array.isArray(rows)||rows.length>1) throw Error('云端数据格式异常');
    this.version=rows[0]?.version??null;
    this.dirty=false;
    return rows[0]?.payload??emptyWorkspace();
  }
  async save(payload) {
    this.dirty=true;
    const next=(this.version??0)+1;
    const rows=await this.request(this.version===null?'POST':'PATCH',this.version===null?'':`?owner_id=eq.${encodeURIComponent(this.uid)}&version=eq.${this.version}`,{owner_id:this.uid,payload,version:next});
    if(!Array.isArray(rows)||rows.length!==1||Number(rows[0].version)!==next) throw Error('另一台设备已更新数据，请导出草稿后重新加载云端数据');
    this.version=next; this.dirty=false;
  }
}

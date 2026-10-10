// Bound both session refresh and network I/O; never send a late write after timeout.
export async function withRequestDeadline(operation, milliseconds=15000) {
  const controller=new AbortController();
  let timer;
  const timeout=new Promise((_,reject)=>{timer=setTimeout(()=>{
    controller.abort();
    reject(Error('云端响应超时，保存结果尚未确认，请保留草稿后重试'));
  },milliseconds)});
  try{return await Promise.race([Promise.resolve().then(()=>operation(controller.signal)),timeout])}
  finally{clearTimeout(timer)}
}

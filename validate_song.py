from pathlib import Path
import sys,json,subprocess,csv,math
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
import mido,numpy as np
from scipy.io import wavfile
out=Path(__file__).parent/'output'
r=json.loads((out/'validation.json').read_text())
for fn in ['instrumental.wav','guide_mix.wav']:
 sr,data=wavfile.read(out/fn); x=data.astype(np.float64)/32768
 assert sr==32000 and data.ndim==2 and data.shape[1]==2
 assert np.isfinite(x).all() and np.max(np.abs(x))<1
 assert np.max(np.abs(x[-100:]))<.001
 r['audio'][fn]={'seconds':len(x)/sr,'peak_dbfs':round(20*math.log10(np.max(np.abs(x))),2),'rms_dbfs':round(20*math.log10(np.sqrt(np.mean(x*x))),2),'channels':2,'last_sample':data[-1].tolist()}
for fn in out.glob('*.mid'):
 m=mido.MidiFile(fn,charset='utf-8')
 for tr in m.tracks:
  pending={}
  for msg in tr:
   assert msg.time>=0
   if msg.type=='set_tempo': assert abs(mido.tempo2bpm(msg.tempo)-170)<.001
   if msg.type=='note_on' and msg.velocity: pending[(msg.channel,msg.note)]=pending.get((msg.channel,msg.note),0)+1
   if msg.type=='note_off' or msg.type=='note_on' and not msg.velocity:
    key=(msg.channel,msg.note); assert pending.get(key,0)>0; pending[key]-=1
  assert not any(pending.values())
rows=list(csv.DictReader((out/'lyrics_timing.csv').open(encoding='utf-8-sig')))
v=mido.MidiFile(out/'vocal_melody.mid',charset='utf-8')
assert len(rows)==sum(x.type=='note_on' and x.velocity>0 for tr in v.tracks for x in tr)==sum(x.type=='lyrics' for tr in v.tracks for x in tr)
for a,b in zip(rows,rows[1:]): assert float(a['start_beat'])+float(a['duration_beats'])<=float(b['start_beat'])+1e-5
for fn in ['guide_mix.wav','instrumental.wav','preview.mp3']:
 p=subprocess.run(['ffmpeg','-hide_banner','-i',str(out/fn),'-af','loudnorm=I=-16:TP=-2:LRA=8:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 start=p.stderr.rfind('{'); metrics=json.loads(p.stderr[start:p.stderr.rfind('}')+1]); r['audio'].setdefault(fn,{})['loudness_lufs']=float(metrics['input_i']); r['audio'][fn]['true_peak_dbtp']=float(metrics['input_tp'])
 assert float(metrics['input_tp'])<0,(fn,metrics)
 r['audio'][fn]['full_decode_valid']=True
r['checks']={'all_midis_readable':True,'no_stuck_notes':True,'tempo_170':True,'mora_note_lyric_event_counts_equal':True,'vocal_notes_monophonic':True,'wav_and_mp3_fully_decoded':True,'true_peak_below_zero':True,'final_tail_fades_to_zero':True}
(out/'validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
print(json.dumps(r,ensure_ascii=False,indent=2))

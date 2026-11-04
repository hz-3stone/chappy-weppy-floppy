#!/usr/bin/env python3
"""Original composition: Chappy Weppy Floppy. Deterministic procedural score and synth."""
from pathlib import Path
import sys, math, csv, json, re, subprocess, os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/chappy-matplotlib")
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
import mido
import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).parent; OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
BPM=170; SPB=60/BPM; SR=32000; PPQ=480
rng=np.random.default_rng(170)
texts={
'Intro':'''チャッピー！ウェッピー！フロッピー！
チャッピー！ウェッピー！フロッピー！
ピー！ピー！ピー！ピー！
ハッピー！ハッピー！ハッピー！''',
'Verse 1':'''チャッピーでハッピーなスヌーピー
ミッフィー、ピッピにピクシー
みんなでピースしてウェッピー
ピーエヌジーからウェッピー！
ピーエイチピーでエーピーアイ
ジーピーユーからシーピーユー
ピーシー、メモリー、コピー、コピー！
ラズパイつないでレッツ・パーティー！''',
'Pre-Chorus':'''ティーシーピー、アイピー！
エフティーピー、エスエフティーピー！
エイチティーティーピー！
エイチティーティーピーエス！
アップしてダウンして
コピーしてチェックして
一致したならハッピー！
不一致だったらアンハッピー！''',
'Chorus':'''チャッピーでウェッピー！
ウェッピーをコピー！
コピーしたウェッピー！
フロッピーにイン！
ハッピーなチャッピー！
スリーピーなスヌーピー！
ハッピーなウェッピー！
フロッピーにイン！
ピー！ピー！ピー！ピー！
チャッピー！ウェッピー！フロッピー！''',
'Verse 2':'''チャッピーに相談ピーエイチピー
エーピーアイからジーピーティー
ウェッピーをチェックしてコピー
ピーシーからフロッピー！
メモリー、ジーピーユー、シーピーユー
エスエスディーからエイチディーディー
ユーエスビーでコピー、コピー！
バックアップしてハッピー！''',
'Pre-Chorus 2':'''アップしてダウンして
チェックしてリトライして
一致したならハッピー！
不一致だったらアンハッピー！''',
'Jugemu Rap':'''チャッピーでハッピーなスヌーピーと
ミッフィーとピッピとピクシーが
ピースしてるウェッピーを作って、
ピーエイチピーでエーピーアイを呼び出して、
ピーシーのメモリーにコピーして、
ジーピーユーでウェッピーを処理して、
シーピーユーで圧縮して、
ディーピーアイを調整して、
ピーエヌジーに変換して、
ピーエヌジーからウェッピーに戻して、
ピーエイチピーでウェッピーをコピーして、
ピーシーのエスエスディーに保存して、
ティーシーピー・アイピーでラズパイに送って、
ラズパイのディスプレーでプレビューして、
エフティーピーでアップロードして、
エスエフティーピーでダウンロードして、
エイチティーティーピーで公開して、
エイチティーティーピーエスで安全に通信して、
ピーエイチピーのエーピーアイから
ジーピーティーにウェッピーを渡して、
ジーピーティーに
「このウェッピーのみんなハッピー？」
って聞いたら、
ジーピーティーが
「ハッピー！」
って答えたので、
ピーエイチピーでレスポンスを受け取って、
ピーシーのディスプレーにハッピーと表示して、
ジーピーエスの位置情報と一緒に
ウェッピーを管理して、
エイチディーディーにバックアップして、
ユーエスビーにコピーして、
ユーエスビーからピーシーにコピーして、
ピーシーからフロッピーにコピーして、
フロッピーに入りきらなかったウェッピーを
チャッピーに相談して圧縮して、
圧縮したウェッピーをフロッピーにコピーして、
フロッピーを別のピーシーにセットして、
ピーエイチピーでチェックサムを計算して、
元のウェッピーと
フロッピーのウェッピーを比較して、
一致したらハッピー！
不一致ならアンハッピー！
アンハッピーならチャッピーに相談して、
チャッピーがピーエイチピーを書き直して、
もう一度ウェッピーをフロッピーにコピーして、
ピーシーでプレビューして、
ジーピーティーにレビューさせて、
ジーピーティーがハッピーと言ったら
チャッピーもハッピー！
スヌーピーもハッピー！
ミッフィーもハッピー！
ピッピもピクシーもハッピー！
ハッピーなウェッピーを保存した
フロッピーを抱えたスヌーピーが
スリーピーになって、
チャッピーもスリーピーになって、
ピーシーもスリープして、
最後に残ったのは……
ハッピーなウェッピーの入ったフロッピー！''',
'Outro':'''チャッピー……
ウェッピー……
フロッピー……
ハッピーなウェッピーの入った……
フロッピー！'''}
texts['Chorus 2']=texts['Chorus']
texts['Final Chorus']='\n'.join(texts['Chorus'].splitlines()[:8])+ '\nハッピーなウェッピーの入ったフロッピー！'
# Kanji readings are explicit: punctuation is not counted as a mora.
readings={'不一致':'ふいっち','一致':'いっち','相談':'そうだん','呼び出':'よびだ','処理':'しょり','圧縮':'あっしゅく','調整':'ちょうせい','変換':'へんかん','戻':'もど','保存':'ほぞん','送':'おく','公開':'こうかい','安全':'あんぜん','通信':'つうしん','渡':'わた','聞':'き','答':'こた','受け取':'うけと','表示':'ひょうじ','位置情報':'いちじょうほう','一緒':'いっしょ','管理':'かんり','入り':'はいり','入った':'はいった','別':'べつ','計算':'けいさん','元':'もと','比較':'ひかく','書き直':'かきなお','もう一度':'もういちど','言':'い','抱':'かか','最後':'さいご','残':'のこ','作':'つく'}
def morae(line):
    for a,b in sorted(readings.items(),key=lambda x:-len(x[0])): line=line.replace(a,b)
    line=''.join(chr(ord(c)+96) if 'ぁ'<=c<='ゖ' else c for c in line)
    out=[]
    for c in line:
        if not ('ァ'<=c<='ヺ' or c=='ー'): continue
        if c in 'ャュョァィゥェォヮ' and out: out[-1]+=c
        else: out.append(c)
    return out
names=['Vocal Melody','Lead Synth','Chords','Bass','Drums','Arpeggio','Counter Melody']
notes={k:[] for k in names}; timings=[]; sections=[]
def note(track,t,d,p,v=90):
    notes[track].append((round(t,6),round(d,6),int(p),int(v)))
# Harmony is changed every bar. A major, relative minor verses; Bb major final.
progressions={'verse':[(54,'m'),(50,'M'),(57,'M'),(52,'M')], 'chorus':[(50,'M'),(52,'M'),(49,'m'),(54,'m'),(50,'M'),(52,'M'),(57,'M'),(57,'M')], 'pre':[(50,'M'),(52,'M'),(54,'m'),(52,'M')], 'rap':[(54,'m'),(50,'M'),(57,'M'),(52,'M')], 'intro':[(57,'M'),(52,'M'),(54,'m'),(50,'M')]}
def kind(s):
    if 'Chorus' in s and not s.startswith('Pre'): return 'chorus'
    if s.startswith('Pre'): return 'pre'
    if s.startswith('Verse'): return 'verse'
    if s=='Jugemu Rap': return 'rap'
    return 'intro'
def chord(sec,local):
    r,q=progressions[kind(sec)][int(local)%len(progressions[kind(sec)])]
    return r+(1 if sec in ('Final Chorus','Outro') else 0),q
# Hooks are scale-degree contours, then adjusted on strong beats to the local chord.
scale=np.array([0,2,4,5,7,9,11])
hook=[4,4,5,4,2,1,2,4, 5,5,4,2,1,2,0,0]
def pitch_for(sec,li,mi,beat,bar):
    shift=1 if sec in ('Final Chorus','Outro') else 0
    root,q=chord(sec,bar); pcs=[root%12,(root+(3 if q=='m' else 4))%12,(root+7)%12]
    if kind(sec)=='rap':
        p=69+shift+[0,0,0,2,0,-2,0,4][(mi+li*2)%8]
    elif kind(sec)=='chorus':
        p=69+shift+int(scale[hook[(mi+ (li%4)*4)%len(hook)]%7])
    elif kind(sec)=='pre': p=69+shift+int(scale[min(6,(li//2+mi//4)%7)])
    elif sec=='Outro': p=69+shift+[7,4,0][li%3]
    else: p=69+shift+int(scale[[0,2,4,2,1,2,4,5][(mi+li)%8]])
    if abs(beat-round(beat))<1e-6 and int(round(beat))%2==0:
        p=min([x for x in range(67+shift,83+shift) if x%12 in pcs],key=lambda x:abs(x-p))
    return p
cursor=0
order=[('Intro',8),('Verse 1',16),('Pre-Chorus',8),('Chorus',16),('Verse 2',16),('Pre-Chorus 2',8),('Chorus 2',16),('Instrumental Break',8),('Jugemu Rap',None),('Final Chorus',16),('Outro',8)]
for sec,bars in order:
    start=cursor; lines=texts.get(sec,'').splitlines()
    if sec=='Jugemu Rap':
        # Mostly continuous sixteenth-note speech, with breathing space per written clause.
        lengths=[math.ceil((len(morae(x))*.25+.5)/2)*2 for x in lines]
        bars=math.ceil(sum(lengths)/4)+2
        offsets=np.cumsum([0]+lengths[:-1]).tolist(); windows=lengths
    elif lines:
        if sec in ('Chorus','Chorus 2'): windows=[6]*8+[4,12]
        elif sec=='Final Chorus': windows=[6]*8+[16]
        elif sec=='Outro': windows=[4,4,4,12,8]
        else: windows=[bars*4/len(lines)]*len(lines)
        offsets=np.cumsum([0]+windows[:-1]).tolist()
    else: offsets=[]; windows=[]
    sections.append({'name':sec,'start_bar':start//4+1,'bars':bars,'start_beat':start,'start_seconds':round(start*SPB,4),'end_seconds':round((start+bars*4)*SPB,4)})
    for li,(line,off,window) in enumerate(zip(lines,offsets,windows)):
        ms=morae(line)
        if sec=='Jugemu Rap': step=.25; onset=0
        else:
            step=min(.5, math.floor((window-.5)/len(ms)*4)/4)
            step=max(.25,step); onset=.0
        assert len(ms)*step <=window, (sec,line,len(ms),window)
        for mi,m in enumerate(ms):
            rel=off+onset+mi*step
            # Leave a held final syllable when the phrase has room.
            dur=step*.82
            if mi==len(ms)-1: dur=min(max(step*.9,window-(mi*step)-.4),1.4 if sec!='Jugemu Rap' else .23)
            p=pitch_for(sec,li,mi,rel,rel//4)
            t=start+rel
            note('Vocal Melody',t,dur,p,103 if mi==0 else 88+mi%3*4)
            timings.append({'section':sec,'line':li+1,'lyric':line,'mora_index':mi+1,'mora':m,'bar':int(t//4)+1,'beat':round(t%4+1,4),'start_beat':t,'start_seconds':round(t*SPB,6),'duration_beats':round(dur,6),'duration_seconds':round(dur*SPB,6),'midi_note':p})
    cursor+=bars*4
TOTAL=cursor
# Arrangement: sparse first rap quarter, then bass, arps, pads and a rising final build.
for S in sections:
    sec=S['name']; start=S['start_beat']; nb=S['bars']; k=kind(sec)
    for b in range(nb):
        t=start+b*4; r,q=chord(sec,b); tri=[r+12,r+(15 if q=='m' else 16),r+19]
        rap=sec=='Jugemu Rap'; prog=b/max(1,nb-1)
        outro=sec=='Outro'; intro=sec=='Intro'; br=sec=='Instrumental Break'
        active=not rap or prog>.22
        full=k=='chorus' or br
        # Last outro bar is a clear tonic cadence with a long release.
        if outro and b>=6:
            if b==6:
                for p in [58,62,65,70]: note('Chords',t,7.4,p,74)
                note('Bass',t,7,34,95); note('Drums',t,.8,49,78)
            continue
        if not rap or prog>.5:
            for hit in ([0,1.5,2.5] if full else [0,2]):
                for p in tri: note('Chords',t+hit,.38 if full else 1.45,p,62 if full else 48)
        if active:
            pat=[(0,0,.45),(.75,0,.22),(1.5,7,.32),(2,0,.45),(2.75,12,.22),(3.5,7,.32)]
            if rap and prog<.5: pat=[(0,0,.7),(2,0,.65)]
            for x,iv,d in pat: note('Bass',t+x,d,r-12+iv,100 if x in (0,2) else 81)
        # Four on the floor, syncopated verse, half-time rap.
        kicks=[0,1,2,3] if full or k=='pre' else [0,1.75,2.5]
        if rap: kicks=[0,2.75] if prog<.75 else [0,1,2,3]
        if intro and b<2: kicks=[0]
        if outro: kicks=[0,2]
        for x in kicks: note('Drums',t+x,.24,36,113)
        for x in ([2] if rap and prog<.5 else [1,3]):
            note('Drums',t+x,.2,38,98); note('Drums',t+x+.015,.18,39,68)
        hats=np.arange(0,4,.25 if full or k=='pre' and b>=nb-2 else .5)
        if rap and prog<.22: hats=[.5,1.5,2.5,3.5]
        for j,x in enumerate(hats):
            note('Drums',t+float(x),.07,46 if full and j%4==2 else 42,55+(j%2==0)*18)
        if b==0 and (full or sec=='Final Chorus'): note('Drums',t,.9,49,92)
        if b%8==7 and (not rap or prog>.75):
            for j in range(6): note('Drums',t+2.5+j*.25,.11,38 if j<4 else 45,62+j*7)
        # Stereo glitter, chord-tone arpeggio; register varies by section.
        if not rap or prog>.42:
            arpseq=[0,1,2,1,0,2,1,2]
            for j in range(16 if full or br else 8):
                x=j*(.25 if full or br else .5)
                p=tri[arpseq[j%8]]+12+(12 if br and j%8>5 else 0)
                note('Arpeggio',t+x,.14 if full else .24,p,56 if full else 46)
        # Lead plays intro calls, instrumental hook, and short answers after sung lines.
        if intro or br or (full and b%4==3) or (outro and b<3):
            for j in range(8):
                p=pitch_for('Chorus',b//2,j,j*.5,b)+(12 if br and b>=4 else 0)
                if outro: p-=0
                note('Lead Synth',t+j*.5,.32,p,72 if full else 88)
        if full and b%4 in (1,3) or (rap and prog>.76):
            for j in range(4): note('Counter Melody',t+2+j*.5,.38,tri[[2,1,0,1][j]]+12,58)
        if (k=='pre' or rap and prog>.9) and b>=nb-2:
            for j in range(16): note('Drums',t+j*.25,.09,38,45+j*3)
# MIDI writer: conductor, UTF-8 lyric events, markers, seven distinct tracks.
channels=[0,1,2,3,9,4,5]; programs=[81,80,90,38,0,80,81]
def save_midi(path,selected):
    mid=mido.MidiFile(type=1,ticks_per_beat=PPQ,charset='utf-8')
    conductor=mido.MidiTrack(); mid.tracks.append(conductor)
    conductor.extend([mido.MetaMessage('track_name',name='170 BPM | Chappy Weppy Floppy'),mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(BPM)),mido.MetaMessage('time_signature',numerator=4,denominator=4),mido.MetaMessage('key_signature',key='A')])
    last=0
    for s in sections:
        tick=int(s['start_beat']*PPQ)
        conductor.append(mido.MetaMessage('marker',text=s['name'],time=tick-last)); last=tick
        if s['name']=='Final Chorus': conductor.append(mido.MetaMessage('key_signature',key='Bb'))
    conductor.append(mido.MetaMessage('end_of_track',time=int(TOTAL*PPQ)-last))
    for name in selected:
        idx=names.index(name); ch=channels[idx]; tr=mido.MidiTrack(); mid.tracks.append(tr)
        tr.append(mido.MetaMessage('track_name',name=name)); tr.append(mido.Message('program_change',channel=ch,program=programs[idx]))
        ev=[]
        for t,d,p,v in notes[name]:
            ev.append((round(t*PPQ),2,mido.Message('note_on',channel=ch,note=p,velocity=v)))
            ev.append((round((t+d)*PPQ),0,mido.Message('note_off',channel=ch,note=p,velocity=0)))
        if name=='Vocal Melody':
            for row in timings: ev.append((round(row['start_beat']*PPQ),1,mido.MetaMessage('lyrics',text=row['mora'])))
        last=0
        for tick,_,msg in sorted(ev,key=lambda e:(e[0],e[1])): tr.append(msg.copy(time=tick-last)); last=tick
        tr.append(mido.MetaMessage('end_of_track',time=max(0,int(TOTAL*PPQ)-last))); mid.save(path)
    if not selected: mid.save(path)
save_midi(OUT/'full_song.mid',names)
for name in names: save_midi(OUT/(name.lower().replace(' ','_')+'.mid'),[name])
with (OUT/'lyrics_timing.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=timings[0].keys()); w.writeheader(); w.writerows(timings)
with (OUT/'structure.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=sections[0].keys()); w.writeheader(); w.writerows(sections)
(OUT/'lyrics.txt').write_text('チャッピー・ウェッピー・フロッピー\nBPM 170 / 4拍子\n\n'+'\n\n'.join('['+s['name']+']\n'+texts.get(s['name'],'（8bitインストゥルメンタル）') for s in sections),encoding='utf-8')
print(json.dumps({'bars':TOTAL/4,'seconds':TOTAL*SPB,'morae':len(timings),'sections':sections},ensure_ascii=False),flush=True)
# Custom band-limited synthesis: no soundfont or network needed during rendering.
N=int((TOTAL*SPB+3.5)*SR); mix=np.zeros((N,2),np.float32); vocal=np.zeros_like(mix)
def synth(p,d,track):
    duration=d*SPB; release=.04 if track in ('Arpeggio','Bass') else .12
    if track=='Chords': release=.22
    n=int((duration+release)*SR); tt=np.arange(n,dtype=np.float32)/SR
    f=440*2**((p-69)/12); phase=2*np.pi*f*tt
    env=np.minimum(tt/.006,1)*np.minimum(np.maximum((duration+release-tt)/release,0),1)
    if track=='Bass':
        y=np.sin(phase)+.30*np.sin(2*phase)+.13*np.sin(3*phase); env*=.65+.35*np.exp(-tt*22)
    elif track=='Chords':
        y=np.zeros(n,np.float32)
        for det in [.997,1.003]:
            for h in range(1,min(10,int(SR/2/f))): y+=np.sin(phase*h*det)/(h*4)
        env*=np.exp(-tt*1.1)
    elif track=='Arpeggio':
        y=np.zeros(n,np.float32)
        for h in [1,3,5,7]:
            if f*h<SR*.46: y+=np.sin(phase*h)/h
        env*=np.exp(-tt*13)
    elif track=='Vocal Melody':
        # Rounded vowel-like lead, with a small vibrato only on held syllables.
        ph=phase+.035*np.sin(2*np.pi*5.4*tt)*np.minimum(tt/.2,1)
        y=np.sin(ph)+.35*np.sin(ph*2)+.18*np.sin(ph*3)+.09*np.sin(ph*5)
        env*=.8+.2*np.exp(-tt*18)
    else:
        y=np.zeros(n,np.float32)
        for h in range(1,9):
            if f*h<SR*.46: y+=np.sin(phase*h)*np.sin(np.pi*h*.32)/h
        env*=.75+.25*np.exp(-tt*12)
    return (y*env).astype(np.float32)
def drum(p):
    dur={36:.34,38:.22,39:.17,42:.065,46:.21,49:1.25,45:.19}.get(p,.15)
    t=np.arange(int(dur*SR),dtype=np.float32)/SR; noise=rng.standard_normal(len(t)).astype(np.float32)
    if p==36:
        ph=2*np.pi*(46*t+105*.018*(1-np.exp(-t/.018)))
        y=np.sin(ph)*np.exp(-t*17)+.15*noise*np.exp(-t*180)
    elif p in (38,39):
        hp=lfilter([1,-1],[1,-.25],noise)
        y=.45*hp*np.exp(-t*(23 if p==38 else 32))+.32*np.sin(2*np.pi*185*t)*np.exp(-t*28)
        if p==39: y*=.7+.3*np.cos(2*np.pi*70*t)
    elif p==45: y=np.sin(2*np.pi*(110*t+2*(1-np.exp(-t*40))))*np.exp(-t*20)
    else:
        hp=lfilter([1,-1],[1,-.5],noise)
        y=hp*np.exp(-t*({42:65,46:19,49:5}[p]))*.25
        y+=.06*np.sin(2*np.pi*6311*t)*np.exp(-t*20)
    return np.asarray(y,dtype=np.float32)
gains={'Vocal Melody':.16,'Lead Synth':.16,'Chords':.125,'Bass':.235,'Drums':.46,'Arpeggio':.105,'Counter Melody':.105}
pans={'Vocal Melody':0,'Lead Synth':-.18,'Chords':.28,'Bass':0,'Drums':0,'Arpeggio':-.52,'Counter Melody':.48}
cache={}
for track in names:
    target=vocal if track=='Vocal Melody' else mix
    for t,d,p,v in notes[track]:
        key=(track,p,round(d,4)) if track!='Drums' else (track,p)
        if key not in cache: cache[key]=drum(p) if track=='Drums' else synth(p,d,track)
        y=cache[key]*gains[track]*(v/100)**1.2
        at=round(t*SPB*SR); end=min(N,at+len(y)); y=y[:end-at]
        pan=pans[track]
        if track=='Drums' and p in (42,46): pan=.26
        lr=[math.sqrt((1-pan)/2),math.sqrt((1+pan)/2)]
        for c in range(2): target[at:end,c]+=y*lr[c]
    print('Rendered',track,len(notes[track]),flush=True)
# Pumping and short stereo delays keep the dense arrangement readable.
beat_phase=(np.arange(N,dtype=np.float32)/SR/SPB)%1
pump=(.78+.22*np.minimum(beat_phase/.22,1)).astype(np.float32)
mix*=pump[:,None]
def space(x,wet):
    out=x.copy()
    for delay,g in [(SPB*.75,wet),(SPB*1.5,wet*.48),(.043,wet*.24),(.079,wet*.19)]:
        n=int(delay*SR); out[n:,0]+=x[:-n,1]*g; out[n:,1]+=x[:-n,0]*g
    return out
mix=space(mix,.15); vocal=space(vocal,.16)
# Soft saturation, shared gain, finite fade only after the deliberate final chord.
full=mix+vocal
peak=float(max(np.max(np.abs(full)),np.max(np.abs(mix))))
gain=.93/peak
for fn,a in [('instrumental.wav',mix),('guide_mix.wav',full)]:
    a=np.tanh(a*gain*1.25)/np.tanh(1.25)*.96
    fade=int(2.2*SR); a[-fade:]*=np.linspace(1,0,fade,dtype=np.float32)[:,None]
    wavfile.write(OUT/fn,SR,(np.clip(a,-1,1)*32767).astype(np.int16))
# Loudness master with true-peak headroom for MP3 encoding.
for fn in ['instrumental.wav','guide_mix.wav']:
    mastered=OUT/('master_'+fn)
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(OUT/fn),'-af','loudnorm=I=-16:TP=-2:LRA=8','-ar',str(SR),'-c:a','pcm_s16le',str(mastered)],check=True)
    mastered.replace(OUT/fn)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(OUT/'guide_mix.wav'),'-codec:a','libmp3lame','-b:a','192k','-metadata','title=チャッピー・ウェッピー・フロッピー','-metadata','artist=Original procedural composition',str(OUT/'preview.mp3')],check=True)
# Verify files by independent MIDI readback and decoded WAV inspection.
report={'bpm':BPM,'time_signature':'4/4','bars':TOTAL//4,'score_duration_seconds':round(TOTAL*SPB,3),'sample_rate':SR,'mora_count':len(timings),'midi':{},'audio':{}}
for path in sorted(OUT.glob('*.mid')):
    m=mido.MidiFile(path,charset='utf-8'); count=0
    for tr in m.tracks:
        active={}
        for msg in tr:
            if msg.type=='note_on' and msg.velocity: active[(msg.channel,msg.note)]=active.get((msg.channel,msg.note),0)+1; count+=1
            if msg.type=='note_off' or msg.type=='note_on' and not msg.velocity:
                key=(msg.channel,msg.note); assert active.get(key,0)>0,(path,key); active[key]-=1
        assert not any(active.values()),path
    tempos=[x.tempo for tr in m.tracks for x in tr if x.type=='set_tempo']; assert all(abs(mido.tempo2bpm(x)-170)<.001 for x in tempos)
    report['midi'][path.name]={'tracks':len(m.tracks),'note_count':count,'duration_seconds':round(m.length,3),'valid':True}
assert len(notes['Vocal Melody'])==len(timings)
assert len([msg for tr in mido.MidiFile(OUT/'vocal_melody.mid',charset='utf-8').tracks for msg in tr if msg.type=='lyrics'])==len(timings)
for a,b in zip(notes['Vocal Melody'],notes['Vocal Melody'][1:]): assert a[0]+a[1]<=b[0]+1e-5
for fn in ['instrumental.wav','guide_mix.wav']:
    sr,data=wavfile.read(OUT/fn); x=data.astype(np.float32)/32768
    assert sr==SR and np.isfinite(x).all() and np.max(np.abs(x))<.999
    report['audio'][fn]={'seconds':len(x)/sr,'peak_dbfs':round(float(20*np.log10(np.max(np.abs(x)))),2),'rms_dbfs':round(float(20*np.log10(np.sqrt(np.mean(x*x)))),2),'channels':x.shape[1],'last_sample':data[-1].tolist()}
rap=[x for x in timings if x['section']=='Jugemu Rap']; report['rap']={'bars':next(s['bars'] for s in sections if s['name']=='Jugemu Rap'),'morae':len(rap),'active_morae_per_second':round(1/(.25*SPB),3),'sixteenth_note_seconds':round(.25*SPB,6)}
report['strong_beat_chord_alignment']={}
for sec in ['Verse 1','Chorus','Final Chorus']:
    ss=next(s for s in sections if s['name']==sec); rows=[r for r in timings if r['section']==sec and (r['start_beat']-ss['start_beat'])%2==0]; good=0
    for row in rows:
        root,q=chord(sec,(row['start_beat']-ss['start_beat'])//4)
        good+=row['midi_note']%12 in [root%12,(root+(3 if q=='m' else 4))%12,(root+7)%12]
    report['strong_beat_chord_alignment'][sec]={'matched':good,'tested':len(rows)}
(OUT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
fig,axs=plt.subplots(3,1,figsize=(16,9),gridspec_kw={'height_ratios':[1,2,2]})
colors=plt.get_cmap('tab20')
for i,s in enumerate(sections):
    axs[0].barh(0,s['end_seconds']-s['start_seconds'],left=s['start_seconds'],color=colors(i),height=.6)
    axs[0].text(s['start_seconds']+.5,0,s['name'].replace(' ','\n'),va='center',fontsize=7)
axs[0].set_yticks([]); axs[0].set_title('Chappy Weppy Floppy | 170 BPM | A major -> Bb major')
x=np.arange(0,len(full),1600)/SR
axs[1].plot(x,full[::1600,0]*gain,linewidth=.45,color='#5968db'); axs[1].set_ylabel('Waveform (pre-master)')
for row in timings: axs[2].plot([row['start_seconds'],row['start_seconds']+row['duration_seconds']],[row['midi_note']]*2,color='#df477d',linewidth=.65)
axs[2].set_ylabel('Vocal MIDI note'); axs[2].set_xlabel('Seconds')
for ax in axs: ax.set_xlim(0,TOTAL*SPB+3.5); ax.grid(alpha=.15)
fig.tight_layout(); fig.savefig(OUT/'song_overview.png',dpi=140); plt.close(fig)
print('DONE',json.dumps(report,ensure_ascii=False),flush=True)

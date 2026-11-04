# ダウンロード

[最新版のReleaseを開く](https://github.com/hz-3stone/chappy-weppy-floppy/releases/latest)

- [全ファイル一式ZIP](https://github.com/hz-3stone/chappy-weppy-floppy/releases/download/v1.0.0/chappy_weppy_floppy.zip)
- [試聴用MP3（シンセのボーカルガイド入り）](https://github.com/hz-3stone/chappy-weppy-floppy/releases/download/v1.0.0/preview.mp3)
- [伴奏WAV](https://github.com/hz-3stone/chappy-weppy-floppy/releases/download/v1.0.0/instrumental.wav)
- [全トラックMIDI](https://github.com/hz-3stone/chappy-weppy-floppy/releases/download/v1.0.0/full_song.mid)

個別のWAV・各パートMIDIもReleaseの **Assets** からダウンロードできます。GitHub自動生成の「Source code」ZIPはソースのみです。音声を含む一式は `chappy_weppy_floppy.zip` を選んでください。

# チャッピー・ウェッピー・フロッピー

Pythonによるオリジナルの高速テクノポップ／チップチューン。BPM 170、4/4、199小節。譜面は4分40.94秒、WAVは残響込み4分44.44秒です。Aメジャーを基調とし、Aメロとラップは相対短調のF#マイナーを交え、大サビでBbメジャーへ半音転調します。

## まず聴く

- `preview.mp3`：シンセによるボーカルガイド入り。通常の音楽プレーヤーやブラウザーで再生できます。
- `guide_mix.wav`：同じガイド入りの非圧縮音声。
- `instrumental.wav`：ボーカルガイドを除いた完成伴奏。コーラスの応答フレーズやリードシンセは含みます。

日本語を発音する歌声は含まれていません。この環境では日本語歌声合成エンジン／歌手音源が見つからなかったため、ボーカルメロディーを母音風のシンセで代用しています。歌声入り版には別途、日本語対応の歌声合成ソフトと歌手音源、歌詞入力・発音調整が必要です。MIDIを読み込むだけで自動的に日本語が発音されるわけではありません。

## ファイル

| ファイル | 内容 |
|---|---|
| full_song.mid | 指定の7楽器トラック＋テンポ・拍子・セクションマーカー用の指揮トラック |
| vocal_melody.mid | Vocal Melody単独。日本語モーラの歌詞メタイベント付き |
| lead_synth.mid | リードシンセ単独 |
| chords.mid | コード単独 |
| bass.mid | ベース単独 |
| drums.mid | GMドラム、チャンネル10 |
| arpeggio.mid | アルペジオ単独 |
| counter_melody.mid | 対旋律単独 |
| instrumental.wav | 32 kHz、16 bit、ステレオの伴奏 |
| guide_mix.wav | 32 kHz、16 bit、ステレオのガイド入りミックス |
| preview.mp3 | ガイド入り、192 kbps、ステレオ |
| lyrics.txt | 実際の構成に展開した全歌詞 |
| lyrics_timing.csv | 全1,588モーラと音符の対応 |
| structure.csv | 各パートの小節数と開始時刻 |
| song_overview.png | 構成・波形・ボーカル音高の全体図 |
| validation.json | 再読み込み・音声デコード・音量などの検証結果 |
| create_song.py / validate_song.py | 生成・検証スクリプト |

## 構成

| パート | 小節数 | 開始時刻 |
|---|---:|---:|
| Intro | 8 | 0:00.00 |
| Verse 1 | 16 | 0:11.29 |
| Pre-Chorus | 8 | 0:33.88 |
| Chorus | 16 | 0:45.18 |
| Verse 2 | 16 | 1:07.76 |
| Pre-Chorus 2 | 8 | 1:30.35 |
| Chorus 2 | 16 | 1:41.65 |
| Instrumental Break | 8 | 2:04.24 |
| Jugemu Rap | 79 | 2:15.53 |
| Final Chorus | 16 | 4:07.06 |
| Outro | 8 | 4:29.65 |

寿限無ラップは歌詞を省略せず79小節に拡張しました。882モーラを基本16分音符（1モーラ約88.24 ms、発音区間で毎秒11.33モーラ）に割り当て、句末に息継ぎを置いています。この速度は生身の歌唱より機械的なボーカルを想定しています。前半はキック・スネア・ハット中心、続いてベース、アルペジオ、コード、対旋律の順に加わります。最後の2小節はフィルと余白を設け、大サビへ接続します。

サビは同じ音高・リズムのフックを2回反復し、大サビでは転調して再現します。「ハッピーなウェッピーの入ったフロッピー！」を大サビ末尾にも追加。アウトロは呼びかけを減らし、最後の「フロッピー！」とBbの終止和音、残響で終了します。

## 歌詞対応表

CSVはUTF-8 BOM付き。`section`、`line`、`lyric`、`mora_index`、`mora`、`bar`、`beat`、`start_beat`、`start_seconds`、`duration_beats`、`duration_seconds`、`midi_note`を含みます。小節・拍は1始まり、通算拍・秒は0始まりです。漢字は明示した読み辞書で変換し、「チャ」「ティ」などの拗音は1モーラ、「ッ」「ン」「ー」は各1モーラとして数えます。句読点は数えません。

1モーラに1ノートを割り当て、全モーラとMIDIの歌詞イベントを一致させています。ただし歌声合成ソフトへ移植する際は、促音「ッ」は無声区間として、長音「ー」は前の母音の延長として扱うなどの編集が必要です。MIDI歌詞はUTF-8のため、古いソフトではCSVまたはlyrics.txtから入力してください。

## 音作りと検証範囲

矩形波風の有限倍音リード、軽いビブラートのガイド、三角波風ベース、短い8bitアルペジオ、合成キック／ノイズスネア／ハットをローカル生成。低域を中央、アルペジオと対旋律を左右に配置し、テンポ同期ディレイを加えています。FFmpegで音量を調整し、MP3エンコードを見越したトゥルーピークの余裕を設けています。

MIDI全8ファイルを再読み込みし、ノートオン／オフ整合性、170 BPM、モノフォニックなボーカル、歌詞イベント数を検証。WAVとMP3はFFmpegで最後までデコードし、ピーク値・無音への終端を確認しています。Aメロ・サビ・大サビの2拍ごとの強拍はコード構成音に一致します。ドラムとベースは共通の拍グリッドから生成。波形と音高図も確認しました。

これらは形式・タイミング・音響値の検証です。「中毒性」「歌いやすさ」といった主観的品質や、人による聴感評価を保証するものではありません。MIDIを一般GM音源で再生すると、このWAV用の独自音色・エフェクトは再現されません。意図した試聴にはMP3またはWAVを使用してください。

## 再生成

Python 3、NumPy、SciPy、Matplotlib、midoとFFmpegが必要です。コードと同じ階層に `output/` が作られます。

```sh
python -m pip install -r requirements.txt
python create_song.py
python validate_song.py
```

外部音源・有料サービス・APIキーは不要です。生成乱数は固定されており再生成可能です。この作業環境ではmidoのみを`/workspace/vendor`に追加し、他は既存のライブラリを使用しました。再生成は既存のoutput内の同名ファイルを上書きします。

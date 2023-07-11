import ppgs
from ppgs.data.download.utils import *
import pypar
import torchaudio
from functools import partial
from tqdm.contrib.concurrent import process_map
import tqdm

def mp3_textgrid(mp3_file: Path, charsiu_wav_dir=None, charsiu_sources=None, charsiu_textgrid_dir=None):
    audio = ppgs.load.audio(mp3_file)
    torchaudio.save(charsiu_wav_dir / (mp3_file.stem + '.wav'), audio, sample_rate=ppgs.SAMPLE_RATE)
    duration = audio.shape[-1] / ppgs.SAMPLE_RATE

    try:
        textgrid_file = charsiu_sources / 'alignments' / (mp3_file.stem + '.TextGrid')
    except:
        textgrid_file = charsiu_sources / 'alignments' / (mp3_file.stem + '.textgrid')

    output_textgrid = charsiu_textgrid_dir / textgrid_file.name

    #Need to fix short format because the textgrid library doesn't understand without
    with open(textgrid_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
    lines[0] = 'File type = "ooTextFile short"\n'
    lines[1] = '"TextGrid"\n'
    with open(output_textgrid, 'w', encoding='utf-8') as outfile:
        outfile.writelines(lines)
    alignment = pypar.Alignment(output_textgrid)
    alignment[-1][-1]._end = duration
    alignment.save(output_textgrid)


def download(common_voice_source=None):
    """Downloads the Charsiu MFA aligned dataset, which includes a subset of Common Voice"""
    charsiu_sources = ppgs.SOURCES_DIR / 'charsiu'
    charsiu_sources.mkdir(parents=True, exist_ok=True)

    # download TextGrid files
    alignments_dir = charsiu_sources / 'alignments'
    alignments_dir.mkdir(parents=True, exist_ok=True)
    download_google_drive_zip('https://drive.google.com/uc?id=1J_IN8HWPXaKVYHaAf7IXzUd6wyiL9VpP', alignments_dir)

    #download Common Voice Subset
    if common_voice_source is None:
        #TODO make this work with directories (who would ever want that?)
        cv_corpus_files = list(ppgs.SOURCES_DIR.glob('cv-corpus*.tar.gz')) + list(ppgs.SOURCES_DIR.glob('cv-corpus*.tgz'))
        if len(cv_corpus_files) >= 1:
            corpus_file = sorted(cv_corpus_files)[-1]
            stems = [file.stem for file in files_with_extension('textgrid', alignments_dir)]
            corpus = tarfile.open(corpus_file, 'r|gz')
            common_voice_dir = charsiu_sources / 'common_voices'
            base_path = Path(list(Path(corpus.next().path).parents)[-2]) #get base directory of tarfile
            clips_path = base_path / 'en' / 'clips' #TODO make language configurable?
            mp3_dir = charsiu_sources / 'mp3'
            mp3_dir.mkdir(exist_ok=True, parents=True)
            print('Scanning tar contents, this can take a long time (>10 minutes)')
            contents = corpus.getnames()
            iterator = tqdm.tqdm(
                stems,
                desc="Extracting common voice clips with corresponding Charsiu alignments",
                total=len(stems),
                dynamic_ncols=True
            )
            stems_not_found = []
            for stem in iterator:
                mp3_path = str(clips_path / (stem + '.mp3'))
                mp3_info = corpus.getmember(mp3_path)
                try:
                    mp3_file = corpus.extractfile(mp3_info)
                    with open(mp3_dir / (stem + '.mp3'), 'wb') as new_mp3_file:
                        import pdb; pdb.set_trace()
                        new_mp3_file.write(mp3_file.read())
                    mp3_file.close()
                except:
                    stems_not_found.append(stem)

        else:
            raise FileNotFoundError(f"""The Common Voice Dataset can only be officially downloaded via https://commonvoice.mozilla.org/en,
            please download this resource and place it in '{ppgs.SOURCES_DIR}'. This command expects a tar.gz or tgz to be present
            or a user provided path using '--common-voice-source' argument""")

def format():
    """Formats the charsiu dataset"""
    charsiu_sources = ppgs.SOURCES_DIR / 'charsiu'

    print("Scanning charsiu for textgrid files (operation may be slow)")
    textgrid_files = files_with_extension('textgrid', charsiu_sources)

    stems = set([f.stem for f in textgrid_files])

    mp3_files = list(files_with_extension('mp3', charsiu_sources))

    found_stems = []
    mp3_found = []
    iterator = tqdm.tqdm(
        mp3_files,
        desc="Scanning Common Voice for mp3 files matching charsiu textgrid labels",
        total=len(mp3_files),
        dynamic_ncols=True
    )

    for mp3_file in iterator:
        if mp3_file.stem in stems:
            found_stems.append(mp3_file.stem)
            mp3_found.append(mp3_file)

    num_not_found = len(stems.difference(set(found_stems)))

    print(f"Failed to find {num_not_found}/{len(stems)} mp3 files ({num_not_found/(len(stems)+1e-6)*100}%)!")

    charsiu_data_dir = ppgs.DATA_DIR / 'charsiu'
    charsiu_wav_dir = charsiu_data_dir / 'wav'
    charsiu_textgrid_dir = charsiu_data_dir / 'textgrid'

    charsiu_wav_dir.mkdir(exist_ok=True, parents=True)
    charsiu_textgrid_dir.mkdir(exist_ok=True, parents=True)

    # iterator = tqdm.tqdm(
    #     mp3_found,
    #     desc="Copying charsiu textgrid files to datasets directory and converting mp3 to wav",
    #     total=len(textgrid_files),
    #     dynamic_ncols=True
    # )

    p = partial(mp3_textgrid, charsiu_wav_dir=charsiu_wav_dir, charsiu_sources=charsiu_sources, charsiu_textgrid_dir=charsiu_textgrid_dir)

    process_map(p, mp3_found, max_workers=16, chunksize=512)
    # iterator = tqdm.tqdm(
    #     mp3_found,
    #     desc="Converting charsiu mp3 files to wav, and writing to datasets directory",
    #     total=len(mp3_found),
    #     dynamic_ncols=True
    # )

    # for mp3_file in iterator:
    #     audio = ppgs.load.audio(mp3_file)
    #     torchaudio.save(charsiu_wav_dir / (mp3_file.stem + '.wav'), audio, sample_rate=ppgs.SAMPLE_RATE)
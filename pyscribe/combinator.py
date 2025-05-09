import os
import wave

from .config import config

class Combinator:

    @staticmethod
    def combine_projects() -> list[str]:
        projects = os.listdir(config.save_path)
        projects = {
            p.rsplit('_', 1)[0]
            for p in projects
            if p.startswith("rec_")
            and len(p.split("_")) == 5
        }

        print("-----------------------")
        print(f"Found {len(projects)} unfinished projects.")
        for p in projects:
            print(f' > {p}')
        print("-----------------------")

        for p in projects:
            Combinator.combine_project(p)
            print()

    @staticmethod
    def combine_project(project: str) -> None:
        print(f'Processing {project} ...')
        files = [
            f for f
            in os.listdir(config.save_path)
            if f.startswith(project)
            and (f.endswith(".wav") or f.endswith(".txt"))
            and len(f.split("_")) == 5
        ]

        # check if there are any .tmp files
        tmp_files = [f for f in files if f.endswith(".tmp")]
        if tmp_files:
            print(f'- Skipping, found {len(tmp_files)} tmp files')
            return
        
        # check if there are any .wav and .txt files
        wav_files = [f for f in files if f.endswith(".wav")]
        txt_files = [f for f in files if f.endswith(".txt")]
        if len(wav_files) != len(txt_files):
            print(f'- Skipping, .wav and .txt files count do not match ({len(wav_files)} != {len(txt_files)})')
            return
        
        # combine all .wav files into one
        print(f'• Combining {len(wav_files)} .wav files...', end='\r')
        combined_wav = os.path.join(config.save_path, f"{project}.wav")
        first_wav_path = os.path.join(config.save_path, wav_files[0])
        total_frames = 0
        with wave.open(first_wav_path, 'rb') as first_wav:
            params = first_wav.getparams()
        with wave.open(combined_wav, 'wb') as combined:
            combined.setparams(params)
            for wav_file in wav_files:
                wav_path = os.path.join(config.save_path, wav_file)
                with wave.open(wav_path, 'rb') as wav:
                    n_frames = wav.getnframes()
                    total_frames += n_frames
                    combined.writeframes(wav.readframes(n_frames))
        print(f'🗸 Combined {len(wav_files)} .wav files.')

        # combine all .txt files into one
        print(f'• Combining {len(txt_files)} .txt files...', end='\r')
        combined_txt = os.path.join(config.save_path, f"{project}.wav.txt")
        text_lengths = 0
        with open(combined_txt, 'w', encoding='utf-8') as combined:
            for txt_file in txt_files:
                txt_path = os.path.join(config.save_path, txt_file)
                with open(txt_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    text_lengths += len(text) + 1
                    combined.write(text)
                    combined.write('\n')
        print(f'🗸 Combined {len(txt_files)} .txt files.')

        # verify combined wav file
        print(f'• Verifying combined files...', end='\r')
        with wave.open(combined_wav, 'rb') as combined:
            n_frames = combined.getnframes()
        valid_wav = n_frames == total_frames
        with open(combined_txt, 'r', encoding='utf-8') as combined:
            text = combined.read()
        valid_txt = len(text) == text_lengths

        if not valid_wav or not valid_txt:
            if not valid_wav:
                print(f'! Warning: Combined wav file has {n_frames} frames, expected {total_frames} frames')
            if not valid_txt:
                print(f'! Warning: Combined txt file has {len(text)} characters, expected {text_lengths} characters')
            
            os.remove(combined_wav)
            os.remove(combined_txt)
            print(f'! Deleted combined wav and txt files')
            return
        print(f'🗸 Verified combined files.')

        if config.remove_after_combine:
            # delete original wav files
            print(f'• Deleting {len(wav_files)} original wav files...', end='\r')
            for wav_file in wav_files:
                wav_path = os.path.join(config.save_path, wav_file)
                os.remove(wav_path)
            print(f'🗸 Deleted {len(wav_files)} original wav files.')
                
            # delete original txt files
            print(f'• Deleting {len(txt_files)} original txt files...', end='\r')
            for txt_file in txt_files:
                txt_path = os.path.join(config.save_path, txt_file)
                os.remove(txt_path)
            print(f'🗸 Deleted {len(txt_files)} original txt files.')
import threading  # For background model loading
import os

class SpeechToTextApp:
    def __init__(self):
        self.device = "None"
        self.transcription_model = None
        self.detect_language_model = None
        self.models_ready = False  # Flag to check if models are loaded

        # Start model loading in the background
        threading.Thread(target=self.preload_models, daemon=True).start()

    def preload_models(self):
        """Preload Whisper models in the background."""
        print("Loading models in the background...")
        import torch
        import whisper

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.detect_language_model = whisper.load_model("large-v2").to(self.device)
        self.transcription_model = whisper.load_model("medium").to(self.device)
        self.models_ready = True
        print("Models loaded successfully!")

    def detect_language(self, audio_path):
        """Detect language using the preloaded model."""
        import whisper
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(self.device)
        _, probs = self.detect_language_model.detect_language(mel)
        detected_language = max(probs, key=probs.get)
        confidence = probs[detected_language]
        print(f"Detected language: {detected_language}, Confidence: {confidence:.2f}")
        return detected_language

    def transcribe_audio(self, chunk_filename, language):
        """Transcribe audio chunk using the preloaded 'medium' model."""
        result = self.transcription_model.transcribe(
            chunk_filename, language=language, task='transcribe', verbose=False
        )
        return result["text"]

    def write_transcript(self, transcript, text_path):
        """Write the final transcript to a file."""
        with open(text_path, "w", encoding="utf-8") as text_file:
            text_file.write(transcript)

    def process_large_audio(self, audio_path, text_path):
        from pydub import AudioSegment
        from tqdm import tqdm

        """Process large audio by splitting it into chunks and transcribing."""
        detected_language = self.detect_language(audio_path)
        audio = AudioSegment.from_mp3(audio_path)
        chunk_length_ms = 10 * 60 * 1000  # 10 minutes in milliseconds
        chunks = list(audio[::chunk_length_ms])
        full_transcript = ""
        total_chunks = len(chunks)

        with tqdm(total=total_chunks, desc="Transcribing", unit="chunk") as pbar:
            for i, chunk in enumerate(chunks):
                chunk_filename = f"chunk_{i}.mp3"
                chunk.export(chunk_filename, format="mp3")

                print(f"Processing chunk {i+1}/{total_chunks}")

                try:
                    chunk_transcript = self.transcribe_audio(chunk_filename, detected_language)
                    full_transcript += chunk_transcript + "\n"
                except Exception as e:
                    print(f"Error transcribing chunk {i+1}: {e}")
                finally:
                    os.remove(chunk_filename)
                pbar.update(1)

        self.write_transcript(full_transcript, text_path)

    def transcribe_mp3_to_text(self, mp3_file_path):
        """Transcribes MP3 file to text."""
        text_file_path = mp3_file_path.rsplit('.', 1)[0] + '.txt'
        try:
            self.process_large_audio(mp3_file_path, text_file_path)
            return text_file_path
        except Exception as e:
            print(f"An error occurred during transcription: {e}")
            return None

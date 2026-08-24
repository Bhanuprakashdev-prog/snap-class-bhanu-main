import numpy as np 
import io
import librosa
import streamlit as st

# Check if Resemblyzer is optionally available, otherwise use Librosa acoustic engine
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
except Exception:
    VoiceEncoder = None
    preprocess_wav = None


@st.cache_resource
def load_voice_encoder():
    if VoiceEncoder is not None:
        try:
            return VoiceEncoder()
        except Exception:
            return None
    return None


def _extract_acoustic_embedding(audio, sr=16000) -> list | None:
    """Extract a robust 128-dimensional L2-normalized acoustic speaker embedding.
    Uses MFCCs (mean, std, max, min) + delta features + spectral statistics.
    """
    try:
        # Trim silence from ends
        trimmed_audio, _ = librosa.effects.trim(audio, top_db=25)
        if len(trimmed_audio) < sr * 0.2:  # at least 200ms of audio
            trimmed_audio = audio

        # 1. 20-order MFCC statistics (80 dims)
        mfcc = librosa.feature.mfcc(y=trimmed_audio, sr=sr, n_mfcc=20)
        f_mfcc = np.concatenate([
            np.mean(mfcc, axis=1),
            np.std(mfcc, axis=1),
            np.max(mfcc, axis=1),
            np.min(mfcc, axis=1)
        ])

        # 2. Delta MFCC statistics (40 dims)
        delta = librosa.feature.delta(mfcc)
        f_delta = np.concatenate([
            np.mean(delta, axis=1),
            np.std(delta, axis=1)
        ])

        # 3. Spectral features (8 dims)
        sc = librosa.feature.spectral_centroid(y=trimmed_audio, sr=sr)
        bw = librosa.feature.spectral_bandwidth(y=trimmed_audio, sr=sr)
        zcr = librosa.feature.zero_crossing_rate(y=trimmed_audio)
        energy_mean = float(np.mean(trimmed_audio ** 2))
        energy_std = float(np.std(trimmed_audio))

        f_spec = np.array([
            float(np.mean(sc)), float(np.std(sc)),
            float(np.mean(bw)), float(np.std(bw)),
            float(np.mean(zcr)), float(np.std(zcr)),
            energy_mean, energy_std
        ])

        # Concatenate: 80 + 40 + 8 = 128 dimensions
        embedding = np.concatenate([f_mfcc, f_delta, f_spec])

        # L2 normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding.tolist()
    except Exception as e:
        st.warning(f"Feature extraction note: {e}")
        return None


def get_voice_embedding(audio_bytes):
    """Generates a 128-dimensional voice embedding vector from raw audio bytes."""
    if not audio_bytes:
        return None

    try:
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)

        # Try Resemblyzer first if active
        encoder = load_voice_encoder()
        if encoder is not None and preprocess_wav is not None:
            try:
                wav = preprocess_wav(audio)
                emb = encoder.embed_utterance(wav)
                return emb.tolist()
            except Exception:
                pass  # Fall back to Librosa acoustic engine

        # High-precision Librosa Acoustic Embedding (128-d)
        return _extract_acoustic_embedding(audio, sr)
    except Exception as e:
        st.error(f"Voice embedding processing error: {e}")
        return None


def identify_speaker(new_embedding, candidates_dict, threshold=0.60):
    """Matches a new embedding against enrolled candidate embeddings via cosine similarity."""
    if new_embedding is None or not candidates_dict:
        return None, 0.0

    new_vec = np.array(new_embedding, dtype=float)
    new_norm = np.linalg.norm(new_vec)
    if new_norm > 0:
        new_vec = new_vec / new_norm

    best_sid = None
    best_score = -1.0

    for sid, stored_embedding in candidates_dict.items():
        if stored_embedding:
            try:
                stored_vec = np.array(stored_embedding, dtype=float)
                # Handle dimension mismatch if any old records exist
                if len(stored_vec) != len(new_vec):
                    min_len = min(len(stored_vec), len(new_vec))
                    stored_vec = stored_vec[:min_len]
                    sub_new_vec = new_vec[:min_len]
                else:
                    sub_new_vec = new_vec

                stored_norm = np.linalg.norm(stored_vec)
                if stored_norm > 0:
                    stored_vec = stored_vec / stored_norm

                similarity = float(np.dot(sub_new_vec, stored_vec))
                if similarity > best_score:
                    best_score = similarity
                    best_sid = sid
            except Exception:
                continue

    if best_score >= threshold:
        return best_sid, round(best_score, 3)

    return None, round(max(0.0, best_score), 3)


def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.60):
    """Processes multi-speaker audio or single-take audio, identifies speakers."""
    if not audio_bytes or not candidates_dict:
        return {}

    try:
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        # Split into non-silent segments (top_db=25)
        segments = librosa.effects.split(audio, top_db=25)
        identified_results = {}

        if len(segments) == 0:
            # If no silence split found, test whole audio
            segments = [(0, len(audio))]

        for start, end in segments:
            if (end - start) < sr * 0.3:  # Skip clips shorter than 300ms
                continue
            segment_audio = audio[start:end]
            embedding = _extract_acoustic_embedding(segment_audio, sr)
            if embedding:
                sid, score = identify_speaker(embedding, candidates_dict, threshold)
                if sid:
                    if sid not in identified_results or score > identified_results[sid]:
                        identified_results[sid] = score

        return identified_results
    except Exception as e:
        st.error(f"Bulk audio analysis failed: {e}")
        return {}
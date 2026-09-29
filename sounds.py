# sounds.py
import os
import pygame


class SoundManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.sounds_dir = os.path.join(self.base_dir, 'sounds')
        self.sounds = {}
        self.music_playing = False
        self.sound_enabled = True

        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except Exception as e:
            print(f"⚠️ Mixer audio non disponible: {e}")
            self.sound_enabled = False

    def _resolve_sound_path(self, filename):
        """Retourne le chemin d'un fichier audio depuis le dossier sounds."""
        if os.path.isabs(filename):
            return filename
        return os.path.join(self.sounds_dir, filename)

    def create_default_sound(self, name):
        """Crée un fichier son silencieux de secours si un fichier manque."""
        if not self.sound_enabled:
            return

        os.makedirs(self.sounds_dir, exist_ok=True)
        default_path = self._resolve_sound_path(f'{name}.wav')

        if os.path.exists(default_path):
            return

        try:
            import math
            import wave

            sample_rate = 22050
            duration = 0.08
            if name in ('correct', 'bonus', 'level_complete'):
                duration = 0.15
            elif name in ('wrong', 'trap'):
                duration = 0.18

            amplitude = 12000
            n_samples = int(sample_rate * duration)

            with wave.open(default_path, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)

                frames = []
                for i in range(n_samples):
                    t = i / sample_rate
                    freq = {'step': 220, 'correct': 660, 'wrong': 80, 'trap': 60, 'bonus': 880, 'level_complete': 440}.get(name, 220)
                    if name == 'wrong':
                        value = math.sin(2 * math.pi * freq * t) * amplitude * (1 - min(t / duration, 1.0))
                    elif name == 'correct':
                        value = math.sin(2 * math.pi * freq * t) * amplitude
                    elif name == 'bonus':
                        value = math.sin(2 * math.pi * freq * t) * amplitude * 0.8
                    elif name == 'level_complete':
                        value = math.sin(2 * math.pi * freq * t) * amplitude * 1.2
                    else:
                        value = math.sin(2 * math.pi * freq * t) * amplitude * 0.4
                    frames.append(int(value).to_bytes(2, byteorder='little', signed=True))

                wav_file.writeframes(b''.join(frames))

            self.sounds[name] = pygame.mixer.Sound(default_path)
        except Exception:
            self.sounds[name] = None

    def load_sounds(self):
        """Charge tous les sons nécessaires."""
        if not self.sound_enabled:
            return

        sound_files = {
            'step': 'step.wav',
            'correct': 'correct.wav',
            'wrong': 'wrong.wav',
            'trap': 'trap.wav',
            'bonus': 'bonus.wav',
            'level_complete': 'level_complete.wav'
        }

        for name, filename in sound_files.items():
            filepath = self._resolve_sound_path(filename)
            try:
                if os.path.exists(filepath):
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                else:
                    self.create_default_sound(name)
            except Exception as e:
                print(f"❌ Erreur chargement son {name}: {e}")
                self.create_default_sound(name)

    def play_sound(self, sound_name, volume=0.5):
        """Joue un son."""
        if not self.sound_enabled or sound_name not in self.sounds or self.sounds[sound_name] is None:
            return

        try:
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play()
        except Exception as e:
            print(f"Erreur lecture son {sound_name}: {e}")

    def play_background_music(self, filepath='background.mp3'):
        """Joue la musique de fond si un fichier est disponible."""
        if not self.sound_enabled:
            return

        music_candidates = []
        if filepath:
            music_candidates.append(self._resolve_sound_path(filepath))
        music_candidates.extend([
            self._resolve_sound_path('background.mp3'),
            self._resolve_sound_path('background.wav'),
        ])

        for music_path in music_candidates:
            if not os.path.exists(music_path):
                continue
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                self.music_playing = True
                return
            except Exception as e:
                print(f"❌ Erreur musique: {e}")

        self.music_playing = False

    def stop_music(self):
        """Arrête la musique."""
        if self.sound_enabled:
            pygame.mixer.music.stop()
        self.music_playing = False

    def toggle_sound(self):
        """Active/désactive les sons."""
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled

    def toggle_music(self):
        """Active/désactive la musique."""
        if self.music_playing:
            self.stop_music()
        else:
            self.play_background_music()
        return self.music_playing
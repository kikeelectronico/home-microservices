import sys
import types

import pytest

try:
    from google.cloud import texttospeech  # noqa: F401
except ModuleNotFoundError:
    google_stub = types.ModuleType("google")
    cloud_stub = types.ModuleType("google.cloud")
    texttospeech_stub = types.ModuleType("google.cloud.texttospeech")

    class AudioEncoding:
        MP3 = "MP3"

    texttospeech_stub.AudioEncoding = AudioEncoding
    texttospeech_stub.TextToSpeechClient = object
    texttospeech_stub.VoiceSelectionParams = lambda **kwargs: kwargs
    texttospeech_stub.AudioConfig = lambda **kwargs: kwargs
    texttospeech_stub.SynthesisInput = lambda **kwargs: kwargs
    google_stub.cloud = cloud_stub
    cloud_stub.texttospeech = texttospeech_stub
    sys.modules["google"] = google_stub
    sys.modules["google.cloud"] = cloud_stub
    sys.modules["google.cloud.texttospeech"] = texttospeech_stub

import Voice


@pytest.fixture
def voice(mocker, monkeypatch):
    tts_client = mocker.MagicMock()
    monkeypatch.setattr(Voice.texttospeech, "TextToSpeechClient", mocker.MagicMock(return_value=tts_client))
    result = Voice.Voice(mocker.MagicMock())
    return result


def test_get_file_synthesizes_and_caches_normalized_filename(voice, tmp_path, monkeypatch, mocker):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "audio").mkdir()
    voice.text_to_speech_client.synthesize_speech.return_value.audio_content = b"mp3-data"
    synthesis_input = mocker.MagicMock()
    monkeypatch.setattr(Voice.texttospeech, "SynthesisInput", synthesis_input)

    path = voice.getFile("Buenos días.")

    assert path == "audio/Buenosdias.mp3"
    assert (tmp_path / path).read_bytes() == b"mp3-data"
    synthesis_input.assert_called_once_with(text="Buenos días.")
    voice.text_to_speech_client.synthesize_speech.assert_called_once_with(
        input=synthesis_input.return_value,
        voice=voice.voice,
        audio_config=voice.audio_config,
    )


def test_get_file_reuses_existing_audio_without_synthesizing(voice, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "audio").mkdir()
    (tmp_path / "audio" / "Hola.mp3").write_bytes(b"cached")

    assert voice.getFile("Hola") == "audio/Hola.mp3"
    voice.text_to_speech_client.synthesize_speech.assert_not_called()


@pytest.mark.parametrize(
    ("states", "expected_room"),
    [
        ([True], "livingroom"),
        ([False, True], "bedroom"),
        ([False, False, True], "bathroom"),
        ([False, False, False], None),
    ],
)
def test_get_room_selects_first_recent_presence(voice, states, expected_room):
    voice.homeware.get.side_effect = [{"last_seen": state} for state in states]

    assert voice.getRoom() == expected_room
    assert voice.homeware.get.call_count == len(states)


def test_play_file_targets_all_speakers(voice, monkeypatch, mocker):
    started = []

    class ImmediateThread:
        def __init__(self):
            pass

        def start(self):
            started.append((self.device_ip, self.file_path))
            self.run()

    run = mocker.patch.object(Voice.subprocess, "run")
    monkeypatch.setattr(Voice.threading, "Thread", ImmediateThread)
    voice.speakers = "all"

    voice.playFile("audio/alert.mp3")

    assert started == [(ip, "audio/alert.mp3") for ip in Voice.DEVICES_IPS.values()]
    assert [call.args[0] for call in run.call_args_list] == [
        ["catt", "-d", ip, "cast", "audio/alert.mp3"] for ip in Voice.DEVICES_IPS.values()
    ]
    assert all(call.kwargs == {"check": True} for call in run.call_args_list)


def test_play_file_targets_room_selected_by_presence(voice, monkeypatch, mocker):
    voice.getRoom = mocker.MagicMock(return_value="bedroom")
    started = []

    class ImmediateThread:
        def __init__(self):
            pass

        def start(self):
            started.append(self.device_ip)
            self.run()

    monkeypatch.setattr(Voice.threading, "Thread", ImmediateThread)
    mocker.patch.object(Voice.subprocess, "run")

    voice.playFile("audio/alert.mp3")

    voice.getRoom.assert_called_once_with()
    assert started == [Voice.DEVICES_IPS["bedroom"]]


def test_get_and_play_resets_speaker_selection(voice, mocker):
    voice.speakers = "all"
    mocker.patch.object(voice, "getFile", return_value="audio/alert.mp3")
    play_file = mocker.patch.object(voice, "playFile")

    voice.getAndPlay("alert")

    voice.getFile.assert_called_once_with("alert")
    play_file.assert_called_once_with("audio/alert.mp3")
    assert voice.speakers == ""


def test_close_closes_text_to_speech_client(voice):
    voice.close()

    voice.text_to_speech_client.close.assert_called_once_with()

import speech_recognition as sr
import time

def debug_listener():
    r = sr.Recognizer()
    
    # 1. Enumerate Mics
    print("=== MICROPHONE LIST ===")
    for i, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"[{i}] {name}")
    print("=======================")

    # 3. Test EVERY Mic
    mics = sr.Microphone.list_microphone_names()
    for i, name in enumerate(mics):
        print(f"\n--- Testing Mic [{i}]: {name} ---")
        try:
            mic = sr.Microphone(device_index=i)
            with mic as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                print(f"Threshold: {r.energy_threshold}")
                
                print("Listening (Speak now!)...")
                try:
                    audio = r.listen(source, timeout=3, phrase_time_limit=3)
                    try:
                        text = r.recognize_google(audio)
                        print(f"--> [SUCCESS] HEARD: '{text}'")
                        print(f"!!! FOUND WORKING MIC: Index {i} !!!")
                        return
                    except sr.UnknownValueError:
                        print("--> [PARTIAL] Detected sound but no words.")
                except sr.WaitTimeoutError:
                    print("--> [SILENCE] No audio.")
        except Exception as e:
            print(f"--> [ERROR] Init failed: {e}")

if __name__ == "__main__":
    debug_listener()

import html
import json
import requests
import subprocess
import time

# For local streaming, the websockets are hosted without ssl - http://
HOST = '127.0.0.1:5001'
URI = f'http://{HOST}/api/v1/generate'

# For reverse-proxied streaming, the remote will likely host with ssl - https://
# URI = 'https://your-uri-here.trycloudflare.com/api/v1/chat'

"""def run(user_input, history):
    request = {
        'user_input': user_input,
        'max_new_tokens': 250,
        'auto_max_new_tokens': False,
        'max_tokens_second': 0,
        'history': history,
        'mode': 'chat-instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'character': None,
        'instruction_template': None,  # Will get autodetected if unset
        'your_name': 'You',
        # 'name1': 'name of user', # Optional
        # 'name2': 'name of character', # Optional
        # 'context': 'character context', # Optional
        # 'greeting': 'greeting', # Optional
        # 'name1_instruct': 'You', # Optional
        # 'name2_instruct': 'Assistant', # Optional
        # 'context_instruct': 'context_instruct', # Optional
        # 'turn_template': 'turn_template', # Optional
        'regenerate': False,
        '_continue': False,
        'chat_instruct_command': 'Make your response different every time.\n\n<|prompt|>',

        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',
        'do_sample': True,
        'temperature': 0.8,
        'top_p': 0.7,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'presence_penalty': 0,
        'frequency_penalty': 0,
        'repetition_penalty_range': 0,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 3,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,
        'grammar_string': '',
        'guidance_scale': 1,
        'negative_prompt': '',

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'custom_token_bans': '',
        'skip_special_tokens': True,
        'stopping_strings': []
    }"""

def run(user_input, history):
    request = {
        'prompt': user_input,
        'max_new_tokens': 250,
        'auto_max_new_tokens': False,
        'max_tokens_second': 0,

        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',
        'do_sample': True,
        'temperature': 2,
        'top_p': 0.9,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'presence_penalty': 0,
        'frequency_penalty': 0,
        'repetition_penalty_range': 2,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 3,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,
        'grammar_string': '',
        'guidance_scale': 1,
        'negative_prompt': '',

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'custom_token_bans': '',
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    """response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['text']
        print(json.dumps(result, indent=4))
        print()
        print(html.unescape(result))
        return html.unescape(result)"""

    response = requests.post(URI, json=request)

    if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
        try:
            result = response.json().get('results', [{}])[0].get('text', "")
            print(json.dumps(result, indent=4))
            return result
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
            return None
        except AttributeError as e:
            print("Attribute error:", e)
            return None
    else:
        print("Error or unexpected response:", response.status_code, response.text)
        return None


if __name__ == '__main__':
    user_input = "Say an interesting fun fact."

    # Basic example
    history = {'internal': [], 'visible': []}

    # "Continue" example. Make sure to set '_continue' to True above
    # arr = [user_input, 'Surely, here is']
    # history = {'internal': [arr], 'visible': [arr]}

    run(user_input)
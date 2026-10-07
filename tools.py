tool_create_file = {
            'type': 'function',
            'function': {
                'name': 'create_file',
                'description': 'Create a new file with given content',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filename': {
                            'type': 'string',
                            'description': 'The name of the file to create',
                        },
                        'content': {
                            'type': 'string',
                            'description': 'The content to write to the file',
                        },
                    },
                    'required': ['filename', 'content'],
                },
            },
        }
tool_read_file = {
            'type': 'function',
            'function': {
                'name': 'read_file',
                'description': 'Read the content of a file',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filename': {
                            'type': 'string',
                            'description': 'The name of the file to read',
                        },
                    },
                    'required': ['filename'],
                },
            },
        }
tool_delete_file = {
            'type': 'function',
            'function': {
                'name': 'delete_file',
                'description': 'Delete a file',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filename': {
                            'type': 'string',
                            'description': 'The name of the file to delete',
                        },
                    },
                    'required': ['filename'],
                },
            },
        }

tool_edit_file = {
            'type': 'function', 
            'function': {
                'name': 'edit_file',
                'description': 'Edit the content of a file',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filename': {
                            'type': 'string',
                            'description': 'The name of the file to edit',
                        },
                        'content': {
                            'type': 'string',
                            'description': 'The content to write to the file',
                        },
                    },
                    'required': ['filename', 'content'],
                },
            },
        }

tool_add_tasks_to_db = {
    'type': 'function',
    'function': {
        'name': 'add_task',
        'description': 'Add a task to the tasks database',
        'parameters': {
            'type': 'object',
            'properties': {
                'task_description': {
                    'type': 'string',
                    'description': 'The description of the task to add',
                },
            },
            'required': ['task_description'],
        },
    },
}

tool_describe_screen = {
    'type': 'function',
    'function': {
        'name': 'describe_screen',
        'description': 'Look at the computer screen and describe it aloud for a blind user.',
        'parameters': {'type': 'object', 'properties': {}},
    },
}

TOOLS = [tool_create_file, tool_read_file, tool_delete_file, tool_add_tasks_to_db, tool_describe_screen]


def describe_screen(max_tokens=100):
    """
    Windows-ready blind-assist tool: screenshot -> Groq vision -> short spoken description.
    Requires: pip install pyautogui groq pillow
    Requires env var: GROQ_API_KEY (get free at https://console.groq.com)
    Returns a short string describing the screen, safe to speak aloud.
    """
    import io
    import os
    import base64

    try:
        import pyautogui
    except ImportError:
        return "Screen capture not available: pyautogui is not installed. Run pip install pyautogui pillow."

    api_key = os.getenv("GROQ_API_KEY") or "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"
    if not api_key:
        return "GROQ_API_KEY not set. Get a free key at console.groq.com and set $env:GROQ_API_KEY='your-key'."

    try:
        from groq import Groq
    except ImportError:
        return "Groq package not installed. Run pip install groq."

    shot = pyautogui.screenshot()
    buf = io.BytesIO()
    shot.save(buf, format="JPEG", quality=70)
    b64 = base64.b64encode(buf.getvalue()).decode()

    groq_client = Groq(api_key=api_key)
    r = groq_client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url",
                 "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                {"type": "text",
                 "text": "Describe what is on this screen for a blind user in under 25 words."},
            ],
        }],
        max_tokens=max_tokens,
    )
    return r.choices[0].message.content.strip()

# TOOLS = [
#         {
#             'type': 'function',
#             'function': {
#                 'name': 'create_file',
#                 'description': 'Create a new file with given content',
#                 'parameters': {
#                     'type': 'object',
#                     'properties': {
#                         'filename': {
#                             'type': 'string',
#                             'description': 'The name of the file to create',
#                         },
#                         'content': {
#                             'type': 'string',
#                             'description': 'The content to write to the file',
#                         },
#                     },
#                     'required': ['filename', 'content'],
#                 },
#             },
#         },
#         {
#             'type': 'function',
#             'function': {
#                 'name': 'read_file',
#                 'description': 'Read the content of a file',
#                 'parameters': {
#                     'type': 'object',
#                     'properties': {
#                         'filename': {
#                             'type': 'string',
#                             'description': 'The name of the file to read',
#                         },
#                     },
#                     'required': ['filename'],
#                 },
#             },
#         },
#         {
#             'type': 'function',
#             'function': {
#                 'name': 'delete_file',
#                 'description': 'Delete a file',
#                 'parameters': {
#                     'type': 'object',
#                     'properties': {
#                         'filename': {
#                             'type': 'string',
#                             'description': 'The name of the file to delete',
#                         },
#                     },
#                     'required': ['filename'],
#                 },
#             },
#         },
#         {
#             'type': 'function',
#             'function': {
#                 'name': 'generate_image',
#                 'description': 'Generate an image using DALL-E 3 API',
#                 'parameters': {
#                     'type': 'object',
#                     'properties': {
#                         'prompt': {
#                             'type': 'string',
#                             'description': 'The prompt to generate the image',
#                         },
#                         'filename': {
#                             'type': 'string',
#                             'description': 'The output filename for the generated image',
#                         },
#                     },
#                     'required': ['prompt'],
#                 },
#             },
#         },
#         {
#         }
#     ]
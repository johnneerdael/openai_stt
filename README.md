# OpenAI Speech-To-Text for Home Assistant

This custom component integrates OpenAI's Speech-to-Text (Whisper) service with Home Assistant, allowing users to convert speech into text. The service supports over 50 languages and can be used with Home Assistant's voice assistant features.

## Description

The OpenAI STT component for Home Assistant makes it possible to use the OpenAI API to transcribe spoken audio to text. This can be used in voice assistants, automations, scripts, or any other component that supports STT within Home Assistant. *You need an OpenAI API key.*

## Features

- Speech-to-Text conversion using OpenAI's Whisper API
- Support for over 50 languages
- Customizable model and transcription settings
- Integration with Home Assistant's voice assistant features

## Installation

### HACS (preferred!)

1. Go to the sidebar HACS menu
2. Click on the 3-dot overflow menu in the upper right and select "Custom Repositories"
3. Copy/paste `https://github.com/johnneerdael/openai_stt` into the "Repository" textbox and select "Integration" for the category
4. Click "Add" to add the custom repository
5. Click on the "OpenAI Speech-to-Text" repository entry and download it
6. Restart Home Assistant to apply the component
7. Add the integration via UI, provide API key and select required settings

### Manual Installation

1. Copy the `custom_components/openai_stt` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Add the integration via UI, provide API key and select required settings

## Configuration

The integration is configured through the UI:

1. Go to Settings -> Devices & Services
2. Click "+ ADD INTEGRATION" and search for "OpenAI Speech-to-Text"
3. Follow the configuration steps:
   - Enter your OpenAI API key
   - Optional: Configure additional settings:
     - Model: The Whisper model to use (default: whisper-1)
     - Prompt: Optional prompt to guide transcription
     - Temperature: Value between 0-1 controlling response creativity (default: 0)

## Supported Languages

This integration supports over 50 languages including: Arabic, Chinese, English, French, German, Italian, Japanese, Korean, Portuguese, Russian, Spanish, and many more.

## Support

For bugs and feature requests, please [open an issue on GitHub](https://github.com/johnneerdael/openai_stt/issues).
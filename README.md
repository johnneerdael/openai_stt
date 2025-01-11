# OpenAI Speech-To-Text for Home Assistant

This custom component integrates [OpenAI Speech-to-Text](https://openai.com/product#whisper), also known as Whisper, into Home Assistant via the OpenAI API.

## Installation

### HACS

1. Go to HACS / Integrations / Three-dots menu / Custom repositories
2. Add:
   - Repository: `https://github.com/johnneerdael/openai_stt_ha`
   - Category: Integration
3. Install the "OpenAI Speech-to-Text" integration
4. Restart Home Assistant

### Manual

1. Copy the `custom_components/openai_stt` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings -> Devices & Services
2. Click the "+ ADD INTEGRATION" button
3. Search for "OpenAI Speech-to-Text"
4. Follow the configuration steps:
   - Enter your OpenAI API key (get one from [OpenAI API Keys](https://platform.openai.com/api-keys))
   - Optional: Configure additional settings:
     - Model: The Whisper model to use (default: whisper-1)
     - Prompt: Optional prompt to guide the transcription
     - Temperature: Value between 0-1 controlling response creativity (default: 0)

## Options

- **API Key** (required): Your OpenAI API key
- **Model** (optional): Currently only `whisper-1` is supported
- **Prompt** (optional): A text prompt to guide the transcription. See [OpenAI documentation](https://platform.openai.com/docs/guides/speech-to-text/prompting)
- **Temperature** (optional): Value between 0 and 1. Higher values make output more creative but less accurate (default: 0)

## Supported Languages

This integration supports over 50 languages including: Arabic, Chinese, English, French, German, Italian, Japanese, Korean, Portuguese, Russian, Spanish, and many more.

## Support

For bugs and feature requests, please [open an issue on GitHub](https://github.com/johnneerdael/openai_stt_ha/issues).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
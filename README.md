# OpenAI Speech-To-Text for Home Assistant

This custom component integrates [OpenAI Speech-to-Text](https://openai.com/product#whisper) (Whisper) into Home Assistant.

## Installation

### HACS

1. Go to HACS / Integrations / Three-dots menu / Custom repositories
2. Add:
   - Repository: `https://github.com/johnneerdael/openai_stt`
   - Category: Integration
3. Install the "OpenAI Speech-to-Text" integration
4. Restart Home Assistant

### Manual

1. Copy the `custom_components/stt` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

Add to your `configuration.yaml`:

```yaml
stt:
  platform: stt
  api_key: YOUR_OPENAI_API_KEY
  # Optional settings:
  model: whisper-1
  prompt: ""
  temperature: 0
```

## Options

- **api_key** (required): Your OpenAI API key
- **model** (optional): Currently only `whisper-1` is supported
- **prompt** (optional): A text prompt to guide the transcription
- **temperature** (optional): Value between 0 and 1 (default: 0)

## Support

For bugs and feature requests, please [open an issue on GitHub](https://github.com/johnneerdael/openai_stt/issues).
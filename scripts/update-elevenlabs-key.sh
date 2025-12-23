#!/bin/bash
# Update ElevenLabs API Key in PAI

echo "🔑 ElevenLabs API Key Update"
echo "============================"
echo ""
echo "Get your API key from: https://elevenlabs.io/app/settings/api-keys"
echo ""
echo "Required permissions:"
echo "  - Text to Speech (tts_read, tts_write)"
echo "  - Voices (voices_read)"
echo ""
read -p "Enter your ElevenLabs API key: " api_key
echo ""

if [ -z "$api_key" ]; then
  echo "❌ No API key provided"
  exit 1
fi

# Backup existing .env
cp /root/.claude/.env /root/.claude/.env.backup

# Update the API key in .env
sed -i "s/^ELEVENLABS_API_KEY=.*/ELEVENLABS_API_KEY=\"$api_key\"/" /root/.claude/.env

echo "✅ API key updated in /root/.claude/.env"
echo "📋 Backup saved to /root/.claude/.env.backup"
echo ""

# Optionally update voice ID
read -p "Do you want to update the default voice ID? (y/N): " update_voice

if [[ $update_voice =~ ^[Yy]$ ]]; then
  echo ""
  echo "To find voice IDs:"
  echo "  1. Go to https://elevenlabs.io/app/voice-library"
  echo "  2. Click on a voice"
  echo "  3. Copy the Voice ID from the URL or settings"
  echo ""
  read -p "Enter voice ID (or press Enter to keep current): " voice_id

  if [ -n "$voice_id" ]; then
    sed -i "s/^ELEVENLABS_VOICE_ID=.*/ELEVENLABS_VOICE_ID=\"$voice_id\"/" /root/.claude/.env
    echo "✅ Voice ID updated"
  fi
fi

echo ""
echo "🧪 Testing the new API key..."
echo ""

# Test the API key
ELEVENLABS_API_KEY="$api_key" bun /root/.claude/scripts/test-voice.ts

echo ""
echo "✅ Setup complete!"

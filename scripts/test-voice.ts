#!/usr/bin/env bun
/**
 * PAI Voice Testing Script
 * Tests ElevenLabs TTS integration for all PAI agents
 */

import { ElevenLabsClient } from "elevenlabs";
import { createWriteStream } from "fs";
import { mkdir } from "fs/promises";
import { join } from "path";

// Load environment variables
const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
const OUTPUT_DIR = "/tmp/pai-voice-tests";

if (!ELEVENLABS_API_KEY) {
  console.error("❌ ELEVENLABS_API_KEY not found in environment");
  process.exit(1);
}

// Agent voice configuration from CORE skill
const AGENT_VOICES = {
  kai: "gNbIwdcnM3B17qzBs2JY",
  "perplexity-researcher": "gNbIwdcnM3B17qzBs2JY",
  "claude-researcher": "gNbIwdcnM3B17qzBs2JY",
  "gemini-researcher": "gNbIwdcnM3B17qzBs2JY",
  pentester: "gNbIwdcnM3B17qzBs2JY",
  engineer: "gNbIwdcnM3B17qzBs2JY",
  "principal-engineer": "gNbIwdcnM3B17qzBs2JY",
  designer: "gNbIwdcnM3B17qzBs2JY",
  architect: "gNbIwdcnM3B17qzBs2JY",
  artist: "gNbIwdcnM3B17qzBs2JY",
  writer: "gNbIwdcnM3B17qzBs2JY",
};

// Test messages for each agent
const TEST_MESSAGES: Record<string, string> = {
  kai: "Hello, I'm Kai, your personal AI assistant. Voice test successful.",
  "perplexity-researcher": "Research agent ready. I can search and analyze information for you.",
  "claude-researcher": "Claude researcher online. Ready to conduct deep research.",
  "gemini-researcher": "Gemini researcher standing by for comprehensive analysis.",
  pentester: "Penetration testing agent activated. Security assessment ready.",
  engineer: "Engineering agent ready for implementation and debugging.",
  "principal-engineer": "Principal engineer ready for architecture and technical decisions.",
  designer: "Design agent ready for UX UI and creative solutions.",
  architect: "Software architect ready for system design and planning.",
  artist: "Creative artist agent ready for visual and creative work.",
  writer: "Writing agent ready for content creation and documentation.",
};

async function testVoice(
  client: ElevenLabsClient,
  agentName: string,
  voiceId: string,
  message: string
): Promise<boolean> {
  try {
    console.log(`\n🎤 Testing ${agentName}...`);
    console.log(`   Voice ID: ${voiceId}`);
    console.log(`   Message: "${message}"`);

    const audio = await client.textToSpeech.convert(voiceId, {
      text: message,
      model_id: "eleven_monolingual_v1",
    });

    // Save to file
    const outputPath = join(OUTPUT_DIR, `${agentName}.mp3`);
    const writeStream = createWriteStream(outputPath);

    // Convert audio stream to buffer and write
    const chunks: Uint8Array[] = [];
    for await (const chunk of audio) {
      chunks.push(chunk);
      writeStream.write(chunk);
    }

    writeStream.end();

    console.log(`   ✅ Success! Saved to: ${outputPath}`);
    console.log(`   📊 Size: ${chunks.reduce((acc, c) => acc + c.length, 0)} bytes`);

    return true;
  } catch (error) {
    console.error(`   ❌ Failed: ${error instanceof Error ? error.message : String(error)}`);
    return false;
  }
}

async function listAvailableVoices(client: ElevenLabsClient) {
  try {
    console.log("\n📋 Available voices in your ElevenLabs account:\n");
    const voices = await client.voices.getAll();

    for (const voice of voices.voices) {
      console.log(`   ${voice.voice_id} - ${voice.name}`);
      if (voice.description) {
        console.log(`      Description: ${voice.description}`);
      }
    }
  } catch (error) {
    console.error(`❌ Failed to list voices: ${error instanceof Error ? error.message : String(error)}`);
  }
}

async function main() {
  console.log("🎙️  PAI Voice System Test\n");
  console.log("=" .repeat(50));

  // Create output directory
  await mkdir(OUTPUT_DIR, { recursive: true });

  // Initialize ElevenLabs client
  const client = new ElevenLabsClient({
    apiKey: ELEVENLABS_API_KEY,
  });

  // List available voices
  await listAvailableVoices(client);

  console.log("\n" + "=".repeat(50));
  console.log("\n🧪 Testing agent voices...\n");

  let successCount = 0;
  let failCount = 0;

  // Test each agent voice
  for (const [agentName, voiceId] of Object.entries(AGENT_VOICES)) {
    const message = TEST_MESSAGES[agentName] || `This is ${agentName} voice test.`;
    const success = await testVoice(client, agentName, voiceId, message);

    if (success) {
      successCount++;
    } else {
      failCount++;
    }

    // Small delay to avoid rate limiting
    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  console.log("\n" + "=".repeat(50));
  console.log("\n📊 Test Results:");
  console.log(`   ✅ Successful: ${successCount}`);
  console.log(`   ❌ Failed: ${failCount}`);
  console.log(`   📁 Output directory: ${OUTPUT_DIR}`);
  console.log("\n💡 To play a test file:");
  console.log(`   mpg123 ${OUTPUT_DIR}/kai.mp3`);
  console.log(`   or`);
  console.log(`   ffplay -nodisp -autoexit ${OUTPUT_DIR}/kai.mp3`);
}

main().catch(console.error);

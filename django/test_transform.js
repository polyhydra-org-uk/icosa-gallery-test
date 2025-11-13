#!/usr/bin/env node

/**
 * Quick test script to verify gltf-transform is working
 */

const fs = require('fs');
const { NodeIO } = require('@gltf-transform/core');
const { dedup, prune } = require('@gltf-transform/functions');

console.log('Testing gltf-transform installation...');
console.log('NodeIO loaded:', typeof NodeIO);
console.log('dedup loaded:', typeof dedup);
console.log('prune loaded:', typeof prune);

async function test() {
  try {
    const io = new NodeIO();
    console.log('✓ NodeIO created successfully');

    console.log('✓ All dependencies loaded correctly!');
    console.log('\nReady to transform glTF files.');
  } catch (error) {
    console.error('✗ Error:', error.message);
    process.exit(1);
  }
}

test();

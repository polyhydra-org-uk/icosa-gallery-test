#!/usr/bin/env node

/**
 * glTF-Transform CLI wrapper for Icosa Gallery
 * Applies various optimization and transformation functions to glTF/GLB files
 */

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const { NodeIO } = require('@gltf-transform/core');
const {
  dedup,
  prune,
  resample,
  quantize,
  weld,
  flatten,
  join,
  instance,
  partition,
  unweld,
  simplify,
  metalRough,
  unlit,
  draco,
  textureCompress,
  meshopt,
} = require('@gltf-transform/functions');
const { ALL_EXTENSIONS } = require('@gltf-transform/extensions');

// Check for optional dependencies
let meshoptimizerAvailable = false;
try {
  require('meshoptimizer');
  meshoptimizerAvailable = true;
  console.log('meshoptimizer: available');
} catch (e) {
  console.warn('meshoptimizer: not available - simplify operation will fail');
}

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 3) {
  console.error('Usage: node gltf_transform.js <input_file> <output_file> <operations>');
  console.error('Operations: comma-separated list of operations to apply');
  console.error('Available operations:');
  console.error('  Core Optimizations:');
  console.error('  - dedup: Remove duplicate vertex or texture data');
  console.error('  - prune: Remove unreferenced properties from the file');
  console.error('  - quantize: Quantize geometry to reduce file size');
  console.error('  - weld: Merge duplicate vertices');
  console.error('  - join: Join compatible primitives');
  console.error('  - flatten: Flatten scene graph hierarchy');
  console.error('  - instance: Create instances of reused meshes');
  console.error('  - resample: Resample animation curves to a consistent framerate');
  console.error('  - metalrough: Convert materials to metallic-roughness workflow');
  console.error('  Additional Operations:');
  console.error('  - partition: Partition binary data into separate files');
  console.error('  - unweld: Unweld vertices (opposite of weld)');
  console.error('  - simplify: Simplify geometry (reduce triangle count)');
  console.error('  - unlit: Convert materials to unlit');
  console.error('  Compression (High Priority):');
  console.error('  - draco: Draco mesh compression');
  console.error('  - textureCompress: KTX2/Basis Universal texture compression');
  console.error('  - meshopt: Meshoptimizer compression');
  process.exit(1);
}

const inputFile = args[0];
const outputFile = args[1];
const operations = args[2].split(',').map(op => op.trim().toLowerCase());

// Additional options (optional, can be passed as JSON string)
let options = {};
if (args[3]) {
  try {
    options = JSON.parse(args[3]);
  } catch (e) {
    console.error('Failed to parse options JSON:', e.message);
    process.exit(1);
  }
}

async function transformGLTF() {
  try {
    // Create IO handler and register all extensions (needed for compression)
    const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);

    // Read the input file
    console.log(`Reading file: ${inputFile}`);
    const document = await io.read(inputFile);

    // Apply transformations in order
    console.log(`Applying operations: ${operations.join(', ')}`);

    for (const operation of operations) {
      console.log(`  - Applying ${operation}...`);

      switch (operation) {
        case 'dedup':
          await document.transform(dedup(options.dedup || {}));
          break;
        case 'prune':
          await document.transform(prune(options.prune || {}));
          break;
        case 'resample':
          await document.transform(resample(options.resample || {}));
          break;
        case 'quantize':
          await document.transform(
            quantize(options.quantize || {
              quantizePosition: 14,
              quantizeNormal: 10,
              quantizeTexcoord: 12,
              quantizeColor: 8,
            })
          );
          break;
        case 'weld':
          await document.transform(
            weld(options.weld || {
              tolerance: 0.0001,
            })
          );
          break;
        case 'flatten':
          await document.transform(flatten(options.flatten || {}));
          break;
        case 'join':
          await document.transform(join(options.join || {}));
          break;
        case 'instance':
          await document.transform(instance(options.instance || {}));
          break;
        case 'partition':
          await document.transform(partition(options.partition || {}));
          break;
        case 'unweld':
          await document.transform(unweld(options.unweld || {}));
          break;
        case 'simplify':
          if (!meshoptimizerAvailable) {
            console.error('ERROR: simplify operation requires meshoptimizer package');
            console.error('Run: npm install meshoptimizer');
            throw new Error('meshoptimizer not installed - simplify operation unavailable');
          }
          if (!options.simplify || !options.simplify.ratio) {
            console.warn('Simplify requires a ratio option (0-1). Using default 0.5');
          }
          await document.transform(
            simplify(options.simplify || { ratio: 0.5, error: 0.001 })
          );
          break;
        case 'metalrough':
          await document.transform(metalRough(options.metalrough || {}));
          break;
        case 'unlit':
          await document.transform(unlit(options.unlit || {}));
          break;
        case 'draco':
          await document.transform(
            draco(options.draco || {
              quantizePosition: 14,
              quantizeNormal: 10,
              quantizeTexcoord: 12,
              quantizeColor: 8,
              quantizeGeneric: 12,
            })
          );
          break;
        case 'texturecompress':
          await document.transform(
            textureCompress(options.textureCompress || {
              encoder: sharp,  // Use sharp for encoding
              targetFormat: 'ktx2',
              slots: /^(baseColor|emissive)$/,  // Compress these texture types
            })
          );
          break;
        case 'meshopt':
          await document.transform(
            meshopt(options.meshopt || {
              level: 'medium',  // Options: low, medium, high
            })
          );
          break;
        default:
          console.warn(`Unknown operation: ${operation}`);
      }
    }

    // Write the output file
    console.log(`Writing file: ${outputFile}`);
    await io.write(outputFile, document);

    console.log('Transformation complete!');

    // Print file size comparison
    const inputStats = fs.statSync(inputFile);
    const outputStats = fs.statSync(outputFile);
    const reduction = ((inputStats.size - outputStats.size) / inputStats.size * 100).toFixed(2);

    console.log(`Input size: ${(inputStats.size / 1024).toFixed(2)} KB`);
    console.log(`Output size: ${(outputStats.size / 1024).toFixed(2)} KB`);
    console.log(`Size reduction: ${reduction}%`);

  } catch (error) {
    console.error('Error during transformation:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

transformGLTF();

import * as fs from 'fs-extra';
import * as path from 'path';
import { glob } from 'glob';
import chalk from 'chalk';
import { ComponentAnalyzer } from '../utils/component-analyzer';
import { SchemaGenerator } from '../utils/schema-generator';

interface SyncOptions {
  path: string;
  output: string;
}

export async function syncCommand(options: SyncOptions) {
  console.log(chalk.blue('🔍 Analyzing React components...'));
  
  try {
    // Ensure the component path exists
    if (!await fs.pathExists(options.path)) {
      console.error(chalk.red(`❌ Component path does not exist: ${options.path}`));
      process.exit(1);
    }

    // Find all TypeScript/TSX files in the components directory
    const componentFiles = await glob('**/*.{ts,tsx}', {
      cwd: options.path,
      absolute: true,
    });

    if (componentFiles.length === 0) {
      console.log(chalk.yellow('⚠️  No component files found'));
      return;
    }

    console.log(chalk.green(`📄 Found ${componentFiles.length} component files`));

    // Analyze each component
    const analyzer = new ComponentAnalyzer();
    const schemaGenerator = new SchemaGenerator();
    const schemas: any[] = [];

    for (const filePath of componentFiles) {
      try {
        console.log(chalk.gray(`   Analyzing ${path.basename(filePath)}...`));
        
        const componentInfo = await analyzer.analyzeComponent(filePath);
        if (componentInfo) {
          const schema = schemaGenerator.generateSchema(componentInfo);
          schemas.push(schema);
          
          console.log(chalk.green(`   ✅ Generated schema for ${componentInfo.name}`));
        }
      } catch (error) {
        console.log(chalk.yellow(`   ⚠️  Skipped ${path.basename(filePath)}: ${error}`));
      }
    }

    // Ensure output directory exists
    await fs.ensureDir(options.output);

    // Write individual schema files
    for (const schema of schemas) {
      const schemaPath = path.join(options.output, `${schema.name}.json`);
      await fs.writeJson(schemaPath, schema, { spaces: 2 });
      console.log(chalk.green(`💾 Saved schema: ${schemaPath}`));
    }

    // Write index file with all schemas
    const indexPath = path.join(options.output, 'index.json');
    await fs.writeJson(indexPath, { schemas }, { spaces: 2 });
    console.log(chalk.green(`📄 Created index: ${indexPath}`));

    console.log(chalk.blue(`\n🎉 Successfully generated ${schemas.length} schemas!`));
    
  } catch (error) {
    console.error(chalk.red('❌ Error during sync:'), error);
    process.exit(1);
  }
}
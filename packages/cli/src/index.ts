#!/usr/bin/env node

import { Command } from 'commander';
import { syncCommand } from './commands/sync';
import { addCommand } from './commands/add';
import chalk from 'chalk';

const program = new Command();

program
  .name('gennie')
  .description('CLI tool for managing gennie UI components and schemas')
  .version('1.0.0');

program
  .command('sync')
  .description('Analyze React components and generate/update JSON schemas')
  .option('-p, --path <path>', 'Path to React components directory', './apps/web/components/ui-components')
  .option('-o, --output <output>', 'Output directory for schemas', './schemas')
  .action(syncCommand);

program
  .command('add')
  .description('Add a new UI component with schema')
  .argument('<name>', 'Component name')
  .option('-c, --category <category>', 'Component category', 'general')
  .action(addCommand);

program.on('command:*', () => {
  console.error(chalk.red(`Invalid command: ${program.args.join(' ')}`));
  console.log(chalk.yellow('Run "gennie --help" for available commands.'));
  process.exit(1);
});

if (process.argv.length === 2) {
  program.help();
}

program.parse(process.argv);
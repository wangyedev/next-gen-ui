import * as fs from 'fs';
import * as path from 'path';
import { Schema, ComponentSchema } from './types';

export class SchemaLoader {
  /**
   * Load schemas from a directory containing individual JSON files
   */
  static async loadFromDirectory(schemasPath: string): Promise<Schema[]> {
    try {
      if (!fs.existsSync(schemasPath)) {
        throw new Error(`Schemas directory does not exist: ${schemasPath}`);
      }

      const files = fs.readdirSync(schemasPath)
        .filter(file => file.endsWith('.json') && file !== 'index.json');

      const schemas: Schema[] = [];
      
      for (const file of files) {
        const filePath = path.join(schemasPath, file);
        const schemaData = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
        schemas.push(schemaData);
      }

      return schemas;
    } catch (error) {
      throw new Error(`Failed to load schemas: ${error}`);
    }
  }

  /**
   * Load schemas from the index.json file
   */
  static async loadFromIndex(indexPath: string): Promise<Schema[]> {
    try {
      if (!fs.existsSync(indexPath)) {
        throw new Error(`Index file does not exist: ${indexPath}`);
      }

      const indexData: ComponentSchema = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
      return indexData.schemas;
    } catch (error) {
      throw new Error(`Failed to load schemas from index: ${error}`);
    }
  }

  /**
   * Filter schemas by category
   */
  static filterByCategory(schemas: Schema[], category: string): Schema[] {
    return schemas.filter(schema => schema.category === category);
  }

  /**
   * Get all available categories
   */
  static getCategories(schemas: Schema[]): string[] {
    const categories = new Set(schemas.map(schema => schema.category));
    return Array.from(categories);
  }

  /**
   * Find schema by component name
   */
  static findByName(schemas: Schema[], name: string): Schema | undefined {
    return schemas.find(schema => 
      schema.name === name || schema.component_name === name
    );
  }
}
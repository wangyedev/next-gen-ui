import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { Schema, QueryRequest, QueryResponse, SDKConfig } from './types';

export class GennieSDK {
  private client: AxiosInstance;
  private schemas: Schema[] = [];

  constructor(config: SDKConfig) {
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        ...(config.apiKey && { 'Authorization': `Bearer ${config.apiKey}` }),
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        const errorMessage = error.response?.data?.error || error.message;
        throw new Error(`API Error: ${errorMessage}`);
      }
    );
  }

  /**
   * Initialize the SDK with schemas
   */
  initialize(schemas: Schema[]): void {
    this.schemas = schemas;
    console.log(`✅ GennieSDK initialized with ${schemas.length} schemas`);
  }

  /**
   * Get all loaded schemas
   */
  getSchemas(): Schema[] {
    return this.schemas;
  }

  /**
   * Get schemas by category
   */
  getSchemasByCategory(category: string): Schema[] {
    return this.schemas.filter(schema => schema.category === category);
  }

  /**
   * Ask a question and get a response with component selection
   */
  async ask(query: string, context?: string): Promise<QueryResponse> {
    if (this.schemas.length === 0) {
      throw new Error('SDK not initialized with schemas. Call initialize() first.');
    }

    try {
      const request: QueryRequest = {
        query,
        context,
        schemas: this.schemas,
      };

      const response: AxiosResponse<QueryResponse> = await this.client.post('/query', request);
      
      return {
        ...response.data,
        success: true,
      };
    } catch (error) {
      return {
        answer: 'I apologize, but I encountered an error processing your request.',
        component: {},
        reasoning: 'Error occurred during API call',
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Health check endpoint
   */
  async health(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      throw new Error(`Health check failed: ${error}`);
    }
  }

  /**
   * Get available component categories
   */
  getCategories(): string[] {
    const categories = new Set(this.schemas.map(schema => schema.category));
    return Array.from(categories);
  }

  /**
   * Find schema by component name
   */
  findSchema(name: string): Schema | undefined {
    return this.schemas.find(schema => 
      schema.name === name || schema.component_name === name
    );
  }

  /**
   * Validate a component against its schema
   */
  validateComponent(componentName: string, data: Record<string, any>): { valid: boolean; errors: string[] } {
    const schema = this.findSchema(componentName);
    if (!schema) {
      return { valid: false, errors: [`Schema not found for component: ${componentName}`] };
    }

    const errors: string[] = [];
    
    // Check required properties
    const requiredProps = schema.tool_definition.parameters.required || [];
    for (const prop of requiredProps) {
      if (!(prop in data)) {
        errors.push(`Missing required property: ${prop}`);
      }
    }

    // Check property types (basic validation)
    for (const [key, value] of Object.entries(data)) {
      const propDef = schema.tool_definition.parameters.properties[key];
      if (propDef) {
        const expectedType = propDef.type;
        const actualType = Array.isArray(value) ? 'array' : typeof value;
        
        if (expectedType !== actualType) {
          errors.push(`Property ${key} expected ${expectedType} but got ${actualType}`);
        }

        // Check enum values
        if (propDef.enum && !propDef.enum.includes(value)) {
          errors.push(`Property ${key} must be one of: ${propDef.enum.join(', ')}`);
        }
      }
    }

    return { valid: errors.length === 0, errors };
  }
}
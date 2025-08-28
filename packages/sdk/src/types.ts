export interface Schema {
  name: string;
  component_name: string;
  category: string;
  description: string;
  properties: SchemaProperty[];
  tool_definition: ToolDefinition;
}

export interface SchemaProperty {
  name: string;
  type: string;
  required: boolean;
  description: string;
  enum?: string[];
  items?: SchemaProperty;
}

export interface ToolDefinition {
  name: string;
  description: string;
  parameters: {
    type: string;
    properties: Record<string, any>;
    required: string[];
  };
}

export interface ComponentSchema {
  schemas: Schema[];
}

export interface QueryRequest {
  query: string;
  context?: string;
  schemas?: Schema[];
}

export interface QueryResponse {
  answer: string;
  component: Record<string, any>;
  reasoning: string;
  success?: boolean;
  error?: string;
}

export interface SDKConfig {
  baseURL: string;
  timeout?: number;
  apiKey?: string;
}
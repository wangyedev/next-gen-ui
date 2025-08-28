import { ComponentInfo, PropInfo } from './component-analyzer';

export interface GeneratedSchema {
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

export class SchemaGenerator {
  generateSchema(componentInfo: ComponentInfo): GeneratedSchema {
    const toolName = `render_${componentInfo.name.toLowerCase().replace(/([A-Z])/g, '_$1').slice(1)}`;
    
    const properties = componentInfo.props.map(prop => this.convertPropToSchemaProperty(prop));
    const requiredProps = componentInfo.props.filter(prop => prop.required).map(prop => prop.name);
    
    const toolParameters: Record<string, any> = {};
    for (const prop of componentInfo.props) {
      toolParameters[prop.name] = this.createParameterDefinition(prop);
    }

    return {
      name: componentInfo.name,
      component_name: componentInfo.name,
      category: componentInfo.category,
      description: componentInfo.description || `Renders a ${componentInfo.name} component`,
      properties,
      tool_definition: {
        name: toolName,
        description: `Render a ${componentInfo.name} component with the provided data`,
        parameters: {
          type: 'object',
          properties: toolParameters,
          required: requiredProps,
        },
      },
    };
  }

  private convertPropToSchemaProperty(prop: PropInfo): SchemaProperty {
    const schemaProperty: SchemaProperty = {
      name: prop.name,
      type: prop.type,
      required: prop.required,
      description: prop.description || `${prop.name} property`,
    };

    // Add specific constraints based on prop names
    if (prop.name === 'chart_type') {
      schemaProperty.enum = ['bar', 'line', 'pie', 'area'];
    }
    if (prop.name === 'variant') {
      schemaProperty.enum = ['default', 'success', 'warning', 'error'];
    }
    if (prop.name === 'icon') {
      schemaProperty.enum = ['sunny', 'cloudy', 'rainy', 'info', 'lightbulb', 'file', 'help'];
    }

    // Handle array types
    if (prop.type === 'array') {
      if (prop.name === 'data') {
        schemaProperty.items = {
          name: 'item',
          type: 'object',
          required: true,
          description: 'Data point with label and value',
        };
      }
      if (prop.name === 'columns') {
        schemaProperty.items = {
          name: 'column',
          type: 'object',
          required: true,
          description: 'Table column definition',
        };
      }
      if (prop.name === 'rows') {
        schemaProperty.items = {
          name: 'row',
          type: 'object',
          required: true,
          description: 'Table row data',
        };
      }
    }

    return schemaProperty;
  }

  private createParameterDefinition(prop: PropInfo): any {
    const definition: any = {
      type: this.mapTypeToJsonSchema(prop.type),
      description: prop.description || `${prop.name} property`,
    };

    // Add specific constraints
    if (prop.name === 'temperature') {
      definition.type = 'number';
      definition.description = 'Temperature in Celsius';
    }
    if (prop.name === 'humidity') {
      definition.type = 'integer';
      definition.minimum = 0;
      definition.maximum = 100;
      definition.description = 'Humidity percentage';
    }
    if (prop.name === 'wind_speed') {
      definition.type = 'number';
      definition.minimum = 0;
      definition.description = 'Wind speed in km/h';
    }
    if (prop.name === 'chart_type') {
      definition.enum = ['bar', 'line', 'pie', 'area'];
    }
    if (prop.name === 'variant') {
      definition.enum = ['default', 'success', 'warning', 'error'];
    }
    if (prop.name === 'data' && prop.type === 'array') {
      definition.type = 'array';
      definition.items = {
        type: 'object',
        properties: {
          label: { type: 'string', description: 'Data point label' },
          value: { type: 'number', description: 'Data point value' },
          color: { type: 'string', description: 'Optional color for the data point' },
        },
        required: ['label', 'value'],
      };
    }
    if (prop.name === 'columns' && prop.type === 'array') {
      definition.type = 'array';
      definition.items = {
        type: 'object',
        properties: {
          key: { type: 'string', description: 'Column identifier' },
          label: { type: 'string', description: 'Column display name' },
          sortable: { type: 'boolean', description: 'Whether column is sortable' },
        },
        required: ['key', 'label'],
      };
    }
    if (prop.name === 'rows' && prop.type === 'array') {
      definition.type = 'array';
      definition.items = {
        type: 'object',
        properties: {
          data: { 
            type: 'object', 
            description: 'Row data as key-value pairs',
            additionalProperties: true,
          },
        },
        required: ['data'],
      };
    }

    return definition;
  }

  private mapTypeToJsonSchema(type: string): string {
    switch (type) {
      case 'number':
        return 'number';
      case 'boolean':
        return 'boolean';
      case 'array':
        return 'array';
      case 'object':
        return 'object';
      default:
        return 'string';
    }
  }
}
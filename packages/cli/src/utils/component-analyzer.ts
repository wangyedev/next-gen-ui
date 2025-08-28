import * as fs from 'fs-extra';
import * as path from 'path';

export interface ComponentInfo {
  name: string;
  filePath: string;
  props: PropInfo[];
  category: string;
  description?: string;
}

export interface PropInfo {
  name: string;
  type: string;
  required: boolean;
  description?: string;
  defaultValue?: any;
}

export class ComponentAnalyzer {
  async analyzeComponent(filePath: string): Promise<ComponentInfo | null> {
    const content = await fs.readFile(filePath, 'utf-8');
    const fileName = path.basename(filePath, '.tsx');
    
    // Skip non-component files
    if (fileName === 'component-renderer' || fileName.includes('index')) {
      return null;
    }

    try {
      // Use regex-based parsing for simplicity
      const componentInfo = this.extractComponentInfoRegex(content, fileName, filePath);
      return componentInfo;
    } catch (error) {
      throw new Error(`Failed to parse ${fileName}: ${error}`);
    }
  }

  private extractComponentInfoRegex(
    content: string,
    fileName: string,
    filePath: string
  ): ComponentInfo | null {
    // Find the main export function using regex
    const exportPattern = /export\s+function\s+(\w+)\s*\(\s*\{([^}]+)\}/;
    const match = content.match(exportPattern);
    
    if (!match) {
      return null;
    }

    const propsString = match[2];
    const props = this.extractPropsFromString(propsString);
    
    // Determine category based on component name
    const category = this.determineCategory(fileName);

    return {
      name: this.convertFileNameToComponentName(fileName),
      filePath,
      props,
      category,
      description: `${fileName.replace(/-/g, ' ')} component`,
    };
  }

  private extractPropsFromString(propsString: string): PropInfo[] {
    const props: PropInfo[] = [];
    
    // Split by comma and extract prop names
    const propNames = propsString
      .split(',')
      .map(prop => prop.trim())
      .filter(prop => prop.length > 0)
      .map(prop => {
        // Remove type annotations and default values
        const cleanProp = prop.split(':')[0].split('=')[0].trim();
        return cleanProp;
      });

    for (const propName of propNames) {
      if (propName) {
        props.push({
          name: propName,
          type: this.inferTypeFromPropName(propName),
          required: !propsString.includes(`${propName}?`) && !propsString.includes(`${propName} =`),
          description: `${propName} property`,
        });
      }
    }

    return props;
  }

  private inferTypeFromPropName(propName: string): string {
    // Basic type inference based on prop names
    if (propName.includes('temperature') || propName.includes('value') || propName.includes('speed')) {
      return 'number';
    }
    if (propName.includes('data') || propName.includes('rows') || propName.includes('columns')) {
      return 'array';
    }
    if (propName.includes('searchable') || propName.includes('sortable') || propName.includes('required')) {
      return 'boolean';
    }
    return 'string';
  }

  private determineCategory(fileName: string): string {
    if (fileName.includes('chart') || fileName.includes('graph')) {
      return 'data_visualization';
    }
    if (fileName.includes('table') || fileName.includes('list')) {
      return 'data_display';
    }
    if (fileName.includes('weather')) {
      return 'data_display';
    }
    if (fileName.includes('info') || fileName.includes('card')) {
      return 'content';
    }
    return 'general';
  }

  private convertFileNameToComponentName(fileName: string): string {
    return fileName
      .split('-')
      .map(part => part.charAt(0).toUpperCase() + part.slice(1))
      .join('');
  }
}
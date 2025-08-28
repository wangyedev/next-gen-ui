"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { GennieSDK, Schema } from '@gennie/sdk';

interface GennieContextType {
  sdk: GennieSDK | null;
  schemas: Schema[];
  isInitialized: boolean;
  error: string | null;
  ask: (query: string, context?: string) => Promise<any>;
}

const GennieContext = createContext<GennieContextType | undefined>(undefined);

interface GennieProviderProps {
  children: ReactNode;
  baseURL?: string;
}

export function GennieProvider({ children, baseURL = 'http://localhost:8000' }: GennieProviderProps) {
  const [sdk, setSdk] = useState<GennieSDK | null>(null);
  const [schemas, setSchemas] = useState<Schema[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function initializeSDK() {
      try {
        setError(null);

        // Create SDK instance
        const sdkInstance = new GennieSDK({
          baseURL,
          timeout: 30000,
        });

        // For now, use mock schemas until we set up proper schema loading
        // In a real implementation, you would fetch from /api/schemas or load from static files
        let loadedSchemas: Schema[] = [];
        
        try {
          // Try to fetch schemas from a static endpoint or use mock data
          const response = await fetch('/schemas/index.json');
          if (response.ok) {
            const schemaData = await response.json();
            loadedSchemas = schemaData.schemas || [];
            console.log(`✅ Loaded ${loadedSchemas.length} schemas from static files`);
          } else {
            throw new Error('Failed to fetch schemas');
          }
        } catch (fetchError) {
          console.warn('⚠️  Could not load schemas from static files, using empty schema set');
          loadedSchemas = [];
        }

        // Initialize SDK with schemas
        sdkInstance.initialize(loadedSchemas);

        setSdk(sdkInstance);
        setSchemas(loadedSchemas);
        setIsInitialized(true);

        console.log('🎉 GennieSDK initialized successfully');

      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error';
        setError(`Failed to initialize GennieSDK: ${errorMessage}`);
        console.error('❌ GennieSDK initialization failed:', err);
      }
    }

    initializeSDK();
  }, [baseURL]);

  const ask = async (query: string, context?: string) => {
    if (!sdk) {
      throw new Error('SDK not initialized');
    }

    try {
      const response = await sdk.ask(query, context);
      return response;
    } catch (err) {
      console.error('Query failed:', err);
      throw err;
    }
  };

  const value: GennieContextType = {
    sdk,
    schemas,
    isInitialized,
    error,
    ask,
  };

  return (
    <GennieContext.Provider value={value}>
      {children}
    </GennieContext.Provider>
  );
}

export function useGennie() {
  const context = useContext(GennieContext);
  if (context === undefined) {
    throw new Error('useGennie must be used within a GennieProvider');
  }
  return context;
}
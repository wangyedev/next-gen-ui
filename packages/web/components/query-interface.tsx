"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Send, MessageSquare, Bot, User, AlertCircle, Loader2 } from "lucide-react";
import { ComponentRenderer } from "@/components/ui-components/component-renderer";
import { apiClient } from "@/lib/api-client";
import { QueryRequest, QueryResponse, ComponentProps } from "@/lib/types";

interface Message {
  id: string;
  type: "user" | "assistant";
  content: string;
  component?: ComponentProps;
  reasoning?: string;
  timestamp: Date;
  loading?: boolean;
  error?: string;
}

export function QueryInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: "assistant",
      content: "Processing your query...",
      timestamp: new Date(),
      loading: true,
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const request: QueryRequest = {
        query: input.trim(),
        context: "",
      };

      const response: QueryResponse = await apiClient.query(request);

      setMessages(prev => prev.slice(0, -1).concat({
        id: (Date.now() + 2).toString(),
        type: "assistant",
        content: response.answer,
        component: response.component as ComponentProps,
        reasoning: response.reasoning,
        timestamp: new Date(),
        error: response.success ? undefined : response.error,
      }));

    } catch (err) {
      console.error("Query failed:", err);
      setMessages(prev => prev.slice(0, -1).concat({
        id: (Date.now() + 3).toString(),
        type: "assistant",
        content: "I apologize, but I encountered an error processing your request.",
        timestamp: new Date(),
        error: err instanceof Error ? err.message : "Unknown error",
      }));
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

  const clearMessages = () => {
    setMessages([]);
    setError(null);
  };

  return (
    <div className="max-w-4xl mx-auto h-full flex flex-col">
      <Card className="flex-1 flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="flex items-center space-x-2">
            <MessageSquare className="h-5 w-5" />
            <span>Multi-Agent Query Interface</span>
          </CardTitle>
          <div className="flex space-x-2">
            <Badge variant="secondary">LangGraph</Badge>
            <Button variant="outline" size="sm" onClick={clearMessages}>
              Clear
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="flex-1 flex flex-col space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <ScrollArea ref={scrollAreaRef} className="flex-1 min-h-[400px] pr-4">
            <div className="space-y-4">
              {messages.length === 0 && (
                <div className="text-center text-muted-foreground py-12">
                  <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium mb-2">Welcome to the Multi-Agent System</p>
                  <p className="text-sm">
                    Ask me anything! I can provide weather information, create charts, display data tables, or answer general questions.
                  </p>
                  <div className="mt-4 space-y-2 text-xs">
                    <p><strong>Examples:</strong></p>
                    <p>• "What's the weather in Paris?"</p>
                    <p>• "Show me sales data for Q1"</p>
                    <p>• "Create a chart of monthly revenue"</p>
                  </div>
                </div>
              )}

              {messages.map((message) => (
                <div key={message.id} className="flex space-x-3">
                  <div className="flex-shrink-0">
                    {message.type === "user" ? (
                      <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                        <User className="h-4 w-4 text-white" />
                      </div>
                    ) : (
                      <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                    )}
                  </div>
                  
                  <div className="flex-1 space-y-2">
                    <div className="bg-muted rounded-lg p-3">
                      {message.loading ? (
                        <div className="flex items-center space-x-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span className="text-sm">{message.content}</span>
                        </div>
                      ) : (
                        <p className="whitespace-pre-wrap">{message.content}</p>
                      )}
                    </div>

                    {message.error && (
                      <Alert variant="destructive">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>{message.error}</AlertDescription>
                      </Alert>
                    )}

                    {message.component && !message.loading && (
                      <div className="space-y-2">
                        <ComponentRenderer component={message.component} />
                        {message.reasoning && (
                          <div className="text-xs text-muted-foreground bg-muted/50 rounded p-2">
                            <strong>Agent Reasoning:</strong> {message.reasoning}
                          </div>
                        )}
                      </div>
                    )}

                    <div className="text-xs text-muted-foreground">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>

          <form onSubmit={handleSubmit} className="flex space-x-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything..."
              disabled={loading}
              className="flex-1"
            />
            <Button type="submit" disabled={loading || !input.trim()}>
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
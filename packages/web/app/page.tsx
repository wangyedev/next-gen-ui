import { QueryInterface } from "@/components/query-interface";

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8 px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold tracking-tight mb-2">
            Multi-Agent UI System
          </h1>
          <p className="text-muted-foreground text-lg">
            Powered by LangGraph • Built with Next.js & shadcn/ui
          </p>
        </div>
        
        <QueryInterface />
      </div>
    </div>
  );
}

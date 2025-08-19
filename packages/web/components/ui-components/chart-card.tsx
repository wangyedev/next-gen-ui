"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartCardProps } from "@/lib/types";
import { BarChart3, TrendingUp, PieChart, Activity } from "lucide-react";

const chartIcons = {
  bar: BarChart3,
  line: TrendingUp,
  pie: PieChart,
  area: Activity,
};

export function ChartCard({
  title,
  chart_type,
  data,
  x_axis_label,
  y_axis_label,
}: Omit<ChartCardProps, "type">) {
  const IconComponent = chartIcons[chart_type];
  const maxValue = Math.max(...data.map(d => d.value));

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-lg font-medium">{title}</CardTitle>
        <IconComponent className="h-6 w-6 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {chart_type === "bar" && (
            <div className="space-y-3">
              {data.map((point, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div className="w-16 text-sm font-medium text-right">{point.label}</div>
                  <div className="flex-1 bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-blue-500 h-4 rounded-full transition-all duration-300"
                      style={{
                        width: `${(point.value / maxValue) * 100}%`,
                        backgroundColor: point.color || "#3b82f6",
                      }}
                    />
                  </div>
                  <div className="w-12 text-sm text-right">{point.value}</div>
                </div>
              ))}
            </div>
          )}

          {chart_type === "pie" && (
            <div className="grid grid-cols-2 gap-4">
              {data.map((point, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: point.color || `hsl(${index * 360 / data.length}, 70%, 50%)` }}
                  />
                  <div className="text-sm">
                    <div className="font-medium">{point.label}</div>
                    <div className="text-muted-foreground">{point.value}</div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {(chart_type === "line" || chart_type === "area") && (
            <div className="space-y-2">
              <div className="flex justify-between items-end h-32 border-l border-b border-gray-200 pl-2 pb-2">
                {data.map((point, index) => (
                  <div key={index} className="flex flex-col items-center space-y-1">
                    <div
                      className="bg-blue-500 w-2 transition-all duration-300"
                      style={{
                        height: `${(point.value / maxValue) * 100}%`,
                        backgroundColor: point.color || "#3b82f6",
                      }}
                    />
                    <div className="text-xs text-center transform -rotate-45 origin-center">
                      {point.label}
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{x_axis_label || "X-Axis"}</span>
                <span>{y_axis_label || "Y-Axis"}</span>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
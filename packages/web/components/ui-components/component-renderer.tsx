"use client";

import { ComponentProps } from "@/lib/types";
import { WeatherCard } from "./weather-card";
import { ChartCard } from "./chart-card";
import { DataTable } from "./data-table";
import { InfoCard } from "./info-card";

interface ComponentRendererProps {
  component: ComponentProps;
}

export function ComponentRenderer({ component }: ComponentRendererProps) {
  if (!component || !component.type) {
    return null;
  }

  switch (component.type) {
    case "weather_card":
      return <WeatherCard {...component} />;
    
    case "chart_card":
      return <ChartCard {...component} />;
    
    case "data_table":
      return <DataTable {...component} />;
    
    case "info_card":
      return <InfoCard {...component} />;
    
    default:
      return (
        <InfoCard
          title="Unknown Component"
          content="The requested component type is not supported."
          variant="error"
        />
      );
  }
}
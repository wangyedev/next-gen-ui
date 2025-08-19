export type ComponentType = "weather_card" | "chart_card" | "data_table" | "info_card";

export type ChartType = "bar" | "line" | "pie" | "area";

export interface WeatherCardProps {
  type: "weather_card";
  location: string;
  temperature: number;
  condition: string;
  humidity?: number;
  wind_speed?: number;
  icon?: string;
}

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface ChartCardProps {
  type: "chart_card";
  title: string;
  chart_type: ChartType;
  data: ChartDataPoint[];
  x_axis_label?: string;
  y_axis_label?: string;
}

export interface TableColumn {
  key: string;
  label: string;
  sortable?: boolean;
}

export interface TableRow {
  data: Record<string, any>;
}

export interface DataTableProps {
  type: "data_table";
  title: string;
  columns: TableColumn[];
  rows: TableRow[];
  searchable?: boolean;
}

export interface InfoCardProps {
  type: "info_card";
  title: string;
  content: string;
  icon?: string;
  variant?: "default" | "success" | "warning" | "error";
}

export type ComponentProps = WeatherCardProps | ChartCardProps | DataTableProps | InfoCardProps;

export interface QueryRequest {
  query: string;
  context?: string;
}

export interface QueryResponse {
  answer: string;
  component: ComponentProps | Record<string, never>;
  reasoning: string;
  success: boolean;
  error?: string;
}
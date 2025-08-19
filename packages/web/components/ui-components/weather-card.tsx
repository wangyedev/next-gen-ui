"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Cloud, Sun, CloudRain, Wind, Droplets } from "lucide-react";
import { WeatherCardProps } from "@/lib/types";

const weatherIcons = {
  sunny: Sun,
  cloudy: Cloud,
  rainy: CloudRain,
  default: Cloud,
};

export function WeatherCard({
  location,
  temperature,
  condition,
  humidity,
  wind_speed,
  icon,
}: Omit<WeatherCardProps, "type">) {
  const IconComponent = icon ? weatherIcons[icon as keyof typeof weatherIcons] || weatherIcons.default : weatherIcons.default;

  return (
    <Card className="w-full max-w-sm">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-lg font-medium">{location}</CardTitle>
        <IconComponent className="h-6 w-6 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="flex items-center space-x-2 mb-4">
          <div className="text-3xl font-bold">{Math.round(temperature)}°C</div>
          <Badge variant="secondary">{condition}</Badge>
        </div>
        
        {(humidity !== undefined || wind_speed !== undefined) && (
          <div className="grid grid-cols-2 gap-4 text-sm">
            {humidity !== undefined && (
              <div className="flex items-center space-x-2">
                <Droplets className="h-4 w-4 text-blue-500" />
                <span>{humidity}%</span>
              </div>
            )}
            {wind_speed !== undefined && (
              <div className="flex items-center space-x-2">
                <Wind className="h-4 w-4 text-gray-500" />
                <span>{wind_speed} km/h</span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
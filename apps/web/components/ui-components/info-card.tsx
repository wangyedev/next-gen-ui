"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Info, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  Lightbulb,
  FileText,
  HelpCircle
} from "lucide-react";
import { InfoCardProps } from "@/lib/types";

const variantStyles = {
  default: "border-border",
  success: "border-green-200 bg-green-50",
  warning: "border-yellow-200 bg-yellow-50",
  error: "border-red-200 bg-red-50",
};

const variantIcons = {
  default: Info,
  success: CheckCircle,
  warning: AlertTriangle,
  error: XCircle,
};

const variantIconColors = {
  default: "text-blue-500",
  success: "text-green-500",
  warning: "text-yellow-500",
  error: "text-red-500",
};

const contentIcons = {
  lightbulb: Lightbulb,
  file: FileText,
  help: HelpCircle,
  info: Info,
};

export function InfoCard({
  title,
  content,
  icon,
  variant = "default",
}: Omit<InfoCardProps, "type">) {
  const VariantIcon = variantIcons[variant];
  const ContentIcon = icon ? contentIcons[icon as keyof typeof contentIcons] : null;

  return (
    <Card className={`w-full ${variantStyles[variant]}`}>
      <CardHeader className="flex flex-row items-center space-y-0 pb-4">
        <div className="flex items-center space-x-2 flex-1">
          {ContentIcon && (
            <ContentIcon className="h-5 w-5 text-muted-foreground" />
          )}
          <CardTitle className="text-lg font-medium">{title}</CardTitle>
        </div>
        <VariantIcon className={`h-5 w-5 ${variantIconColors[variant]}`} />
      </CardHeader>
      <CardContent>
        <div className="prose prose-sm max-w-none">
          <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
            {content}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
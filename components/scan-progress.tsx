"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, XCircle, Clock, Loader2 } from "lucide-react"

interface ScanStatus {
  scan_id: string
  phone_number: string
  status: string
  progress: number
  features: Record<string, string>
  started_at: string
  completed_at?: string
  errors: Array<{
    feature: string
    error: string
    timestamp: string
  }>
}

interface ScanProgressProps {
  scanStatus: ScanStatus
}

const featureLabels: Record<string, string> = {
  basic_info: "📋 Basic Info",
  geolocation: "🌍 Geolocation",
  owner_spam: "👤 Owner & Spam",
  messaging: "💬 Messaging Apps",
  social_media: "📱 Social Media",
  breach_data: "🔓 Breach Data",
  spam_reports: "⚠️ Spam Reports",
  domain_whois: "🌐 Domain/WHOIS",
  profile_images: "🖼️ Profile Images",
  reassignment: "🔄 Reassignment",
  online_mentions: "🔍 Online Mentions",
}

export function ScanProgress({ scanStatus }: ScanProgressProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-400" />
      case "failed":
        return <XCircle className="h-4 w-4 text-red-400" />
      case "running":
        return <Loader2 className="h-4 w-4 text-blue-400 animate-spin" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return "bg-green-400/20 text-green-400 border-green-400/20"
      case "failed":
        return "bg-red-400/20 text-red-400 border-red-400/20"
      case "running":
        return "bg-blue-400/20 text-blue-400 border-blue-400/20"
      default:
        return "bg-gray-400/20 text-gray-400 border-gray-400/20"
    }
  }

  return (
    <Card className="bg-black/50 border-green-400/20 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-green-400">
          <span>Scan Progress: {scanStatus.phone_number}</span>
          <Badge variant="outline" className={getStatusColor(scanStatus.status)}>
            {scanStatus.status.toUpperCase()}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-green-400/70">Overall Progress</span>
            <span className="text-green-400">{scanStatus.progress}%</span>
          </div>
          <Progress value={scanStatus.progress} className="bg-black/50 border border-green-400/20" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {Object.entries(scanStatus.features).map(([feature, status]) => (
            <div
              key={feature}
              className="flex items-center gap-2 p-3 rounded-lg bg-black/30 border border-green-400/10"
            >
              {getStatusIcon(status)}
              <span className="text-sm text-green-400/90">{featureLabels[feature] || feature}</span>
            </div>
          ))}
        </div>

        {scanStatus.errors.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-red-400">Errors:</h4>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {scanStatus.errors.map((error, index) => (
                <div key={index} className="text-xs p-2 rounded bg-red-500/10 border border-red-500/20 text-red-400">
                  <strong>{featureLabels[error.feature] || error.feature}:</strong> {error.error}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="text-xs text-green-400/50 space-y-1">
          <div>Started: {new Date(scanStatus.started_at).toLocaleString()}</div>
          {scanStatus.completed_at && <div>Completed: {new Date(scanStatus.completed_at).toLocaleString()}</div>}
        </div>
      </CardContent>
    </Card>
  )
}

"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Download, ChevronDown, ChevronRight, FileJson, FileText } from "lucide-react"

interface ScanResultsProps {
  results: any
}

export function ScanResults({ results }: ScanResultsProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set())

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(section)) {
      newExpanded.delete(section)
    } else {
      newExpanded.add(section)
    }
    setExpandedSections(newExpanded)
  }

  const downloadFile = async (fileType: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/download/${results.phone_number}/${fileType}`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = `${results.phone_number}.${fileType}`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error("Download failed:", error)
    }
  }

  const renderValue = (value: any): string => {
    if (value === null || value === undefined) return "N/A"
    if (Array.isArray(value)) return value.length > 0 ? value.join(", ") : "None"
    if (typeof value === "object") return JSON.stringify(value, null, 2)
    return String(value)
  }

  const sectionIcons: Record<string, string> = {
    basic_info: "📋",
    geolocation: "🌍",
    owner_spam: "👤",
    messaging_presence: "💬",
    social_media_profiles: "📱",
    breach_data: "🔓",
    spam_reports: "⚠️",
    domain_whois: "🌐",
    profile_images: "🖼️",
    number_reassignment: "🔄",
    online_mentions: "🔍",
  }

  const formatSectionName = (section: string) => {
    return section
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ")
  }

  const hasData = (data: any) => {
    if (!data || typeof data !== "object") return false
    return Object.values(data).some(
      (value) => value !== null && value !== undefined && (Array.isArray(value) ? value.length > 0 : value !== ""),
    )
  }

  return (
    <div className="space-y-6">
      <Card className="bg-black/50 border-green-400/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center justify-between text-green-400">
            <span>📊 Scan Results: {results.phone_number}</span>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => downloadFile("json")}
                className="bg-green-400/20 hover:bg-green-400/30 text-green-400 border-green-400/20"
              >
                <FileJson className="h-4 w-4 mr-1" />
                JSON
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => downloadFile("csv")}
                className="bg-blue-400/20 hover:bg-blue-400/30 text-blue-400 border-blue-400/20"
              >
                <FileText className="h-4 w-4 mr-1" />
                CSV
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => downloadFile("pdf")}
                className="bg-purple-400/20 hover:bg-purple-400/30 text-purple-400 border-purple-400/20"
              >
                <Download className="h-4 w-4 mr-1" />
                PDF
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-green-400/70">Scanned on: {new Date(results.scan_date).toLocaleString()}</div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {Object.entries(results).map(([section, data]) => {
          if (["phone_number", "scan_date", "errors"].includes(section)) return null

          const isExpanded = expandedSections.has(section)
          const dataExists = hasData(data)

          return (
            <Card key={section} className="bg-black/50 border-green-400/20 backdrop-blur-sm">
              <Collapsible>
                <CollapsibleTrigger onClick={() => toggleSection(section)} className="w-full">
                  <CardHeader className="hover:bg-green-400/5 transition-colors">
                    <CardTitle className="flex items-center justify-between text-left">
                      <div className="flex items-center gap-2">
                        <span>{sectionIcons[section] || "📄"}</span>
                        <span className="text-green-400">{formatSectionName(section)}</span>
                        {dataExists && (
                          <Badge variant="outline" className="bg-green-400/20 text-green-400 border-green-400/20">
                            Data Found
                          </Badge>
                        )}
                      </div>
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 text-green-400" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-green-400" />
                      )}
                    </CardTitle>
                  </CardHeader>
                </CollapsibleTrigger>

                <CollapsibleContent>
                  <CardContent className="pt-0">
                    {dataExists ? (
                      <div className="space-y-3">
                        {Object.entries(data as Record<string, any>).map(([key, value]) => (
                          <div key={key} className="grid grid-cols-1 md:grid-cols-3 gap-2">
                            <div className="text-sm font-medium text-green-400/90">
                              {key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}:
                            </div>
                            <div className="md:col-span-2 text-sm text-green-400/70 break-all">
                              {renderValue(value)}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-green-400/50">No data found for this section</div>
                    )}
                  </CardContent>
                </CollapsibleContent>
              </Collapsible>
            </Card>
          )
        })}
      </div>

      {results.errors && results.errors.length > 0 && (
        <Card className="bg-red-500/10 border-red-500/20 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-red-400">⚠️ Errors Encountered</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {results.errors.map((error: any, index: number) => (
                <div key={index} className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                  <div className="text-sm font-medium text-red-400">
                    {error.feature}: {error.error}
                  </div>
                  <div className="text-xs text-red-400/70 mt-1">{new Date(error.timestamp).toLocaleString()}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

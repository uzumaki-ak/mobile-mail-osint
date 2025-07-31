"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2, Phone, Search } from "lucide-react"
import { ScanProgress } from "./scan-progress"
import { ScanResults } from "./scan-results"

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

export function PhoneScanner() {
  const [phoneNumber, setPhoneNumber] = useState("")
  const [isScanning, setIsScanning] = useState(false)
  const [scanStatus, setScanStatus] = useState<ScanStatus | null>(null)
  const [scanResults, setScanResults] = useState<any>(null)
  const [error, setError] = useState("")

  const startScan = async () => {
    if (!phoneNumber.trim()) {
      setError("Please enter a phone number")
      return
    }

    setError("")
    setIsScanning(true)
    setScanStatus(null)
    setScanResults(null)

    try {
      const response = await fetch("http://localhost:8000/api/scan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ phone_number: phoneNumber }),
      })

      if (!response.ok) {
        throw new Error("Failed to start scan")
      }

      const data = await response.json()
      const scanId = data.scan_id

      // Poll for status updates
      const pollStatus = async () => {
        try {
          const statusResponse = await fetch(`http://localhost:8000/api/scan/${scanId}/status`)
          if (statusResponse.ok) {
            const status = await statusResponse.json()
            setScanStatus(status)

            if (status.status === "completed") {
              // Get final results
              const resultsResponse = await fetch(`http://localhost:8000/api/scan/${scanId}/results`)
              if (resultsResponse.ok) {
                const results = await resultsResponse.json()
                setScanResults(results)

                // Save to localStorage
                const savedScans = JSON.parse(localStorage.getItem("phoneScans") || "[]")
                savedScans.unshift({
                  phone_number: phoneNumber,
                  scan_date: new Date().toISOString(),
                  status: "completed",
                  results: results,
                })
                localStorage.setItem("phoneScans", JSON.stringify(savedScans.slice(0, 50))) // Keep last 50
              }
              setIsScanning(false)
            } else if (status.status === "failed") {
              setError("Scan failed: " + (status.error || "Unknown error"))
              setIsScanning(false)
            } else {
              // Continue polling
              setTimeout(pollStatus, 2000)
            }
          }
        } catch (err) {
          console.error("Status polling error:", err)
          setTimeout(pollStatus, 5000) // Retry after 5 seconds
        }
      }

      pollStatus()
    } catch (err) {
      setError("Failed to start scan: " + (err as Error).message)
      setIsScanning(false)
    }
  }

  const formatPhoneNumber = (value: string) => {
    // Remove all non-digits
    const digits = value.replace(/\D/g, "")

    // Format as international number
    if (digits.length > 0) {
      if (digits.startsWith("1") && digits.length === 11) {
        return `+1 ${digits.slice(1, 4)} ${digits.slice(4, 7)} ${digits.slice(7)}`
      } else if (digits.length >= 10) {
        return `+${digits}`
      }
    }
    return value
  }

  return (
    <div className="space-y-6">
      <Card className="bg-black/50 border-green-400/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-400">
            <Phone className="h-5 w-5" />
            Phone Number Scanner
          </CardTitle>
          <CardDescription className="text-green-400/70">
            Enter a phone number to start comprehensive OSINT analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              type="tel"
              placeholder="+1 555 123 4567"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(formatPhoneNumber(e.target.value))}
              className="bg-black/50 border-green-400/20 text-green-400 placeholder:text-green-400/50"
              disabled={isScanning}
            />
            <Button
              onClick={startScan}
              disabled={isScanning || !phoneNumber.trim()}
              className="bg-green-400/20 hover:bg-green-400/30 text-green-400 border border-green-400/20"
            >
              {isScanning ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Scanning...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 mr-2" />
                  Start Scan
                </>
              )}
            </Button>
          </div>

          {error && <div className="p-3 rounded-lg bg-red-500/20 border border-red-500/20 text-red-400">{error}</div>}
        </CardContent>
      </Card>

      {scanStatus && <ScanProgress scanStatus={scanStatus} />}

      {scanResults && <ScanResults results={scanResults} />}
    </div>
  )
}
